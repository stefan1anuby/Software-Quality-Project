const API_BASE = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.getElementById('teachers-table-body');
  const jsonOutput = document.getElementById('teachers-json');
  const form = document.getElementById('teacher-form');
  const nameInput = document.getElementById('teacher-name');

  async function loadTeachers() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/timetable/teachers/`);
      if (!res.ok) throw new Error('Failed to fetch teachers');
      const teachers = await res.json();

      // Clear and populate table
      tableBody.innerHTML = '';
      teachers.forEach(teacher => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${teacher.id}</td>
          <td>${teacher.name}</td>
        `;
        tableBody.appendChild(row);
      });

      // Render raw JSON
      jsonOutput.textContent = JSON.stringify(teachers, null, 2);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="2">Error loading teachers</td></tr>`;
      jsonOutput.textContent = err.message;
    }
  }
  loadTeachers();
  });
