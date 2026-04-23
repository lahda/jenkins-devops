async function loadTasks() {
  const res = await fetch('/api/tasks');
  const data = await res.json();

  document.getElementById("total").textContent = data.tasks.length;
  document.getElementById("done").textContent = data.tasks.filter(t => t.status === "done").length;
  document.getElementById("pending").textContent = data.tasks.filter(t => t.status === "pending").length;

  document.getElementById("list").innerHTML =
    data.tasks.map(t => `<p>${t.title}</p>`).join('');
}

async function addTask() {
  const title = document.getElementById("title").value;

  await fetch("/api/tasks", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title})
  });

  loadTasks();
}

loadTasks();