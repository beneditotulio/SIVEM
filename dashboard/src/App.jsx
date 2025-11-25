import { useEffect, useState } from "react";
import { getHealth, predict } from "./services/api";

export default function App() {
  const [status, setStatus] = useState("...");
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    getHealth().then((d) => setStatus(d.status));
  }, []);

  async function handlePredict() {
    const r = await predict([0, 0, 0]);
    setPrediction(r.prediction ?? r.error);
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>SIVEM Dashboard</h1>
      <p>API: {status}</p>
      <button onClick={handlePredict}>Testar Previsão</button>
      {prediction !== null && <p>Resultado: {String(prediction)}</p>}
    </div>
  );
}