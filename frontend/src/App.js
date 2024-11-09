import logo from './logo.svg';
import './App.css';

function Button({ text }) {
  return (
    <button>{text}</button>
  )
}

function Greeting({ name }) {
  return (
    <h1>Hello,{name}</h1>
  )
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Greeting name="world" />
        <Button text="hoge" />
      </header>
    </div>
  );
}

export default App;
