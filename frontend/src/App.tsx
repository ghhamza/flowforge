import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { WorkflowEditor } from "@/pages/WorkflowEditor";
import { WorkflowList } from "@/pages/WorkflowList";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WorkflowList />} />
        <Route path="/workflows/:id" element={<WorkflowEditor />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
