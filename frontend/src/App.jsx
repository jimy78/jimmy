import React, {useState} from "react";
import axios from "axios";

export default function App(){
  const [msg, setMsg] = useState("");
  const [history, setHistory] = useState([]);

  const send = async () => {
    if(!msg) return;
    setHistory(h => [...h, {from:"user", text: msg}]);
    setMsg("");
    try{
      const res = await axios.post("/chat", {message: msg});
      setHistory(h => [...h, {from:"bot", text: res.data.reply}]);
    }catch(e){
      setHistory(h => [...h, {from:"bot", text: "Erreur de connexion"}]);
    }
  };

  return (
    <div style={{padding:20,fontFamily:'Arial, sans-serif'}}>
      <h2>HR Agent Prototype</h2>
      <div style={{height:300, overflow:"auto", border:"1px solid #ddd", padding:10, marginBottom:10}}>
        {history.map((m,i)=>(<div key={i}><b>{m.from}:</b> {m.text}</div>))}
      </div>
      <input value={msg} onChange={e=>setMsg(e.target.value)} style={{width:"80%", padding:8}}/>
      <button onClick={send} style={{marginLeft:8, padding:'8px 12px'}}>Envoyer</button>
    </div>
  );
}