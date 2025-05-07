const API_BASE = 'http://localhost:8000';

// Function to load the timetable for the selected group
async function loadTimetable() {
  const groupName = document.getElementById('group-select').value;

  try {
    const url = `${API_BASE}/api/v1/timetable/schedule/?group_name=${groupName}`;
    console.log(`Request URL: ${url}`);

    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    console.log('Fetched data:', data);

    const tableBody = document.getElementById('timetable-body');
    tableBody.innerHTML = '';

    if (data.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9">No timetable available for this group.</td></tr>';
    }

    data.forEach(entry => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${entry.id}</td>
        <td>${entry.day_of_week}</td>
        <td>${entry.start_hour}:00</td>
        <td>${entry.end_hour}:00</td>
        <td>${entry.subject_id}</td>
        <td>${entry.room_id}</td>
        <td>${entry.teacher_id}</td>
        <td>${entry.student_group_id !== null ? entry.student_group_id : '-'}</td>
        <td>
          <button type="button" onclick="deleteEntry(${entry.id})" 
            style="background-color:#d9534f; color:white; border:none; padding:0.5rem 1rem; border-radius:6px;">
            Delete
          </button>
        </td>`;
      tableBody.appendChild(row);
    });

    document.getElementById('timetable-raw').textContent = JSON.stringify(data, null, 2);

  } catch (err) {
    console.error('Error loading timetable:', err);
    document.getElementById('timetable-raw').textContent = `Error: ${err.message}`;
  }
}

// Function to delete a schedule entry by ID
async function deleteEntry(id) {
  if (!confirm(`Are you sure you want to delete schedule entry ID ${id}?`)) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/timetable/schedule/${id}`, {
      method: 'DELETE'
    });

    if (res.status === 204) {
      alert(`Entry ${id} deleted successfully.`);
      loadTimetable(); // Reload the table
    } else {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete entry.');
    }
  } catch (err) {
    alert('Error: ' + err.message);
  }
}

// Automatically load timetable when page is ready
window.addEventListener('DOMContentLoaded', () => {
  loadTimetable();

  // ✅ ADDITION: Handle form-based deletion
  const deleteForm = document.getElementById('delete-form');
  if (deleteForm) {
    deleteForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const idInput = document.getElementById('delete-id');
      const id = parseInt(idInput.value);
      if (!id) return alert('Please enter a valid ID.');
      await deleteEntry(id);
      e.target.reset();
    });
  }
});
