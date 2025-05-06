const API_BASE = 'http://localhost:8000';

// Function to load the timetable for the selected group
async function loadTimetable() {
  // Get the selected group name
  const groupName = document.getElementById('group-select').value;
  
  try {
    // Construct the URL with the selected group name
    const url = `${API_BASE}/api/v1/timetable/schedule/?group_name=${groupName}`;
    console.log(`Request URL: ${url}`); // Log the URL to verify it's correct

    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    console.log('Fetched data:', data); // Log the fetched data

    // Clear any existing rows in the timetable
    const tableBody = document.getElementById('timetable-body');
    tableBody.innerHTML = '';

    if (data.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="8">No timetable available for this group.</td></tr>';
    }

    // Render each entry in the timetable
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
      `;
      tableBody.appendChild(row);
    });

    // Render raw JSON response in the <pre> element
    document.getElementById('timetable-raw').textContent = JSON.stringify(data, null, 2);

  } catch (err) {
    console.error('Error loading timetable:', err);
    document.getElementById('timetable-raw').textContent = `Error: ${err.message}`;
  }
}

// Automatically load timetable when page is ready
window.addEventListener('DOMContentLoaded', () => {
  // Initial load for the default group (Group A)
  loadTimetable();
});
