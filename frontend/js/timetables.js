const API_BASE = 'http://localhost:8000';

// Function to load the timetable for the selected group
export const loadTimetable = async () => {
  const groupSelect = document.getElementById('group-select');
  const tableBody = document.getElementById('timetable-body');
  const rawOutput = document.getElementById('timetable-raw');

  // Preconditions
  console.assert(groupSelect, '#group-select is required');
  console.assert(tableBody, '#timetable-body is required');
  console.assert(rawOutput, '#timetable-raw is required');

  const groupName = groupSelect.value;
  console.assert(groupName.trim(), 'Group name must not be empty');

  try {
    const url = `${API_BASE}/api/v1/timetable/schedule/?group_name=${groupName}`;
    console.log(`Request URL: ${url}`);

    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();

    // Postconditions
    console.assert(Array.isArray(data), 'Expected timetable data to be an array');
    console.assert(
      data.every(entry => 'id' in entry && 'day_of_week' in entry),
      'Each entry must contain required fields'
    );

    console.log('Fetched data:', data);

    tableBody.innerHTML = '';

    if (data.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9">No timetable available for this group.</td></tr>';
      return;
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

    // Postcondition
    console.assert(
      tableBody.children.length === data.length,
      'Table rows must match number of entries'
    );

    rawOutput.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    console.error('Error loading timetable:', err);
    rawOutput.textContent = `Error: ${err.message}`;
    console.assert(
      rawOutput.textContent.startsWith('Error:'),
      'Raw output should show error message on failure'
    );
  }
};

// Function to delete a schedule entry by ID
export const deleteEntry = async (id) => {
  console.assert(typeof id === 'number' && id > 0, 'ID must be a positive number');

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
};

// Automatically load timetable when page is ready
window.addEventListener('DOMContentLoaded', () => {
  loadTimetable();

  const deleteForm = document.getElementById('delete-form');
  const idInput = document.getElementById('delete-id');

  // Preconditions
  console.assert(deleteForm, '#delete-form is expected (if delete is enabled)');
  console.assert(idInput, '#delete-id is required input');

  if (deleteForm && idInput) {
    deleteForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = parseInt(idInput.value);
      console.assert(!isNaN(id), 'ID input must be a valid number');

      if (!id) return alert('Please enter a valid ID.');

      await deleteEntry(id);
      e.target.reset();
    });
  }
});
