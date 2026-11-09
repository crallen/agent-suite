import { useState } from "react";
import Home from "./pages/Home.jsx";

const pages = {
  home: { title: "Home", component: Home },
};

export default function App() {
  const [page, setPage] = useState("home");
  const Page = pages[page].component;

  return (
    <div className="app">
      <nav className="app-nav">
        {Object.entries(pages).map(([key, { title }]) => (
          <button
            key={key}
            className={key === page ? "active" : undefined}
            onClick={() => setPage(key)}
          >
            {title}
          </button>
        ))}
      </nav>
      <main className="app-main">
        <Page />
      </main>
    </div>
  );
}
