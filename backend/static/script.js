const API_URL = "/comments/";

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("commentForm");
  const taskIdInput = document.getElementById("taskId");
  const contentInput = document.getElementById("content");
  const commentsList = document.getElementById("commentsList");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const task_id = parseInt(taskIdInput.value);
    const content = contentInput.value;

    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id, content }),
    });

    if (res.ok) {
      loadComments();
      form.reset();
    }
  });

  async function loadComments() {
    const res = await fetch(API_URL);
    const comments = await res.json();

    commentsList.innerHTML = "";

    comments.forEach((comment) => {
      const div = document.createElement("div");
      div.className = "comment";

      const input = document.createElement("input");
      input.value = comment.content;

      const saveBtn = document.createElement("button");
      saveBtn.textContent = "Save";
      saveBtn.onclick = async () => {
        await fetch(`${API_URL}${comment.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: input.value }),
        });
        loadComments();
      };

      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = "Delete";
      deleteBtn.onclick = async () => {
        await fetch(`${API_URL}${comment.id}`, {
          method: "DELETE",
        });
        loadComments();
      };

      div.appendChild(input);
      div.appendChild(saveBtn);
      div.appendChild(deleteBtn);
      commentsList.appendChild(div);
    });
  }

  loadComments();
});
