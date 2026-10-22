const API_BASE = "/api";
const ticketList = document.querySelector("#ticket-list");
const notice = document.querySelector("#notice");
const ticketCount = document.querySelector("#ticket-count");
const statusFilter = document.querySelector("#status-filter");
const form = document.querySelector("#ticket-form");
let tickets = [];

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.classList.toggle("error", isError);
  notice.hidden = !message;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "The request could not be completed.");
  }
  return payload;
}

function renderTickets() {
  const filter = statusFilter.value;
  const visibleTickets = tickets.filter(
    (ticket) => filter === "all" || ticket.status === filter,
  );
  ticketCount.textContent = String(tickets.length);
  ticketList.replaceChildren();

  if (tickets.length === 0) {
    ticketList.innerHTML =
      '<div class="empty-state"><span class="empty-icon">✓</span><h3>No tickets yet</h3><p>Create a ticket above to get started.</p></div>';
    return;
  }

  if (visibleTickets.length === 0) {
    ticketList.innerHTML =
      '<div class="empty-state compact"><h3>No matching tickets</h3><p>Try another status filter.</p></div>';
    return;
  }

  for (const ticket of visibleTickets) {
    const card = document.createElement("article");
    card.className = "ticket-card";

    const main = document.createElement("div");
    main.className = "ticket-main";
    const id = document.createElement("span");
    id.className = "ticket-id";
    id.textContent = `#${ticket.id}`;
    const title = document.createElement("h3");
    title.textContent = ticket.title;
    main.append(id, title);

    const metadata = document.createElement("div");
    metadata.className = "ticket-metadata";
    const priority = document.createElement("span");
    priority.className = `priority priority-${ticket.priority}`;
    priority.textContent = `${ticket.priority} priority`;

    const statusLabel = document.createElement("label");
    statusLabel.className = "status-control";
    statusLabel.textContent = "Status";
    const select = document.createElement("select");
    select.setAttribute("aria-label", `Status for ticket ${ticket.id}`);
    for (const status of ["open", "doing", "done"]) {
      const option = document.createElement("option");
      option.value = status;
      option.textContent = status[0].toUpperCase() + status.slice(1);
      option.selected = ticket.status === status;
      select.append(option);
    }
    select.addEventListener("change", () => updateStatus(ticket, select));
    statusLabel.append(select);
    metadata.append(priority, statusLabel);
    card.append(main, metadata);
    ticketList.append(card);
  }
}

async function loadTickets() {
  try {
    tickets = await request("/tickets");
    showNotice("");
    renderTickets();
  } catch (error) {
    showNotice(`Unable to load tickets: ${error.message}`, true);
  }
}

async function updateStatus(ticket, select) {
  const previousStatus = ticket.status;
  select.disabled = true;
  try {
    const updated = await request(`/tickets/${ticket.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: select.value }),
    });
    tickets = tickets.map((item) => (item.id === updated.id ? updated : item));
    showNotice(`Ticket #${updated.id} status saved.`);
    renderTickets();
  } catch (error) {
    select.value = previousStatus;
    select.disabled = false;
    showNotice(`Unable to update ticket: ${error.message}`, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = form.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  showNotice("");
  try {
    const formData = new FormData(form);
    const created = await request("/tickets", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title"),
        priority: formData.get("priority"),
      }),
    });
    tickets.push(created);
    form.reset();
    document.querySelector("#priority").value = "medium";
    statusFilter.value = "all";
    renderTickets();
    showNotice(`Ticket #${created.id} created.`);
  } catch (error) {
    showNotice(`Unable to create ticket: ${error.message}`, true);
  } finally {
    submitButton.disabled = false;
  }
});

statusFilter.addEventListener("change", renderTickets);
loadTickets();
