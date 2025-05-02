const API_BASE = 'http://localhost:8000';

async function loadTimetable() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/timetable/schedule/`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // Render table
    const tableBody = document.getElementById('timetable-body');
    tableBody.innerHTML = '';
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

    // Render raw JSON
    document.getElementById('timetable-raw').textContent = JSON.stringify(data, null, 2);

  } catch (err) {
    console.error('Error loading timetable:', err);
    document.getElementById('timetable-raw').textContent = `Error: ${err.message}`;
  }
}

window.addEventListener('DOMContentLoaded', loadTimetable);
