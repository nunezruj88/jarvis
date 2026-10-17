import test from 'node:test';
import assert from 'node:assert/strict';
import {defaults,validateConfig,runTool,chat,createServer,testAI} from '../server.mjs';

test('prueba de IA devuelve respuesta real y rechaza respuestas vacías o errores',async()=>{
 const result=await testAI({...defaults,model:'prueba'},async()=>({content:'OK real'}));
 assert.equal(result.reply,'OK real');assert.equal(result.model,'prueba');assert.ok(result.elapsedMs>=0);
 await assert.rejects(()=>testAI(defaults,async()=>({content:''})),/no devolvió/);
 await assert.rejects(()=>testAI(defaults,async()=>{throw Error('HTTP 401');}),/401/);
});

test('configuración: conserva, elimina y sustituye credenciales sin perder el modelo',()=>{
 const old={...defaults,apiKey:'old',model:'chosen'};
 assert.equal(validateConfig({apiKey:''},old).apiKey,'old');
 assert.equal(validateConfig({clearApiKey:true},old).apiKey,'');
 assert.equal(validateConfig({clearApiKey:true,apiKey:'new'},old).apiKey,'new');
 assert.equal(validateConfig({},old).model,'chosen');
 assert.throws(()=>validateConfig({baseUrl:'http://example.com/v1'}));
 assert.throws(()=>validateConfig({latitude:91}));
 assert.throws(()=>validateConfig({haUrl:'http://user:secret@localhost'}));
});
test('Home Assistant filtra entidades antes de enviarlas al modelo',async()=>{
 const c={...defaults,entities:['light.salon']};
 const io={haStates:async()=>[{entity_id:'light.salon',state:'on'},{entity_id:'person.private',state:'home'}]};
 const result=await runTool('home_states',c,io);
 assert.deepEqual(result.states,[{entity_id:'light.salon',state:'on'}]);
 await assert.rejects(()=>runTool('home_states',defaults,io),/Selecciona/);
 await assert.rejects(()=>runTool('turn_on',c,io),/no permitida/);
});
test('el tiempo usa coordenadas configuradas y devuelve observación actual',async()=>{
 await assert.rejects(()=>runTool('weather',defaults),/localidad/);
 let url;
 const result=await runTool('weather',{...defaults,city:'Prueba',latitude:40,longitude:-3},{requestJson:async u=>{url=u;return {current:{temperature_2m:20},current_units:{},timezone:'Europe/Madrid'};}});
 assert.match(url,/latitude=40/);assert.equal(result.city,'Prueba');assert.equal(result.current.temperature_2m,20);
});
test('chat ejecuta consulta y entrega el resultado fresco al modelo',async()=>{
 let calls=0;
 const result=await chat({text:'¿Está encendida la luz?'},defaults,{
  ai:async(c,m)=>{if(calls++===0)return {content:null,tool_calls:[{id:'1',type:'function',function:{name:'home_states',arguments:'{}'}}]};assert.equal(m.at(-1).role,'tool');assert.match(m.at(-1).content,/on/);return {content:'Está encendida.'};},
  runTool:async()=>({kind:'home',states:[{entity_id:'light.salon',state:'on'}]})
 });
 assert.equal(result.reply,'Está encendida.');assert.equal(result.cards.length,1);
});
test('fallos de herramientas se comunican al modelo y nunca producen tarjetas falsas',async()=>{
 let calls=0;
 const result=await chat({text:'Mi casa'},defaults,{ai:async(c,m)=>{if(calls++===0)return {tool_calls:[{id:'1',type:'function',function:{name:'home_states'}}]};assert.match(m.at(-1).content,/desconectado/);return {content:'Home Assistant está desconectado.'};},runTool:async()=>{throw Error('desconectado');}});
 assert.deepEqual(result.cards,[]);
});
test('servidor: UI disponible, secretos inaccesibles y acceso entre orígenes bloqueado',async()=>{
 const server=createServer();await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const url=`http://127.0.0.1:${server.address().port}`;
 try{
  assert.equal((await fetch(url)).status,200);
  assert.equal((await fetch(url+'/config.local.json')).status,404);
  assert.equal((await fetch(url+'/api/config')).status,403);
  assert.equal((await fetch(url+'/api/config',{headers:{'X-Jarvis-Client':'local',Origin:'https://other.test'}})).status,403);
  const c=await (await fetch(url+'/api/config',{headers:{'X-Jarvis-Client':'local'}})).json();assert.equal('apiKey' in c,false);assert.equal('haToken' in c,false);
 }finally{await new Promise(resolve=>server.close(resolve));}
});
