import logo from './logo.svg';
import './App.css';
import { useLocation } from 'react-router-dom';

function App() {
    const location = useLocation();
    const params = new URLSearchParams(location.search);
    const foo = params.get('foo');
    const baz = params.get('baz');
    return (
        <div className="App">
          <p>foo: {foo}</p>
          <p>baz: {baz}</p>
        </div>
    );
}

export default App;
