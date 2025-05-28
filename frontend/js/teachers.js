const API_BASE = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.getElementById('teachers-table-body');
  const jsonOutput = document.getElementById('teachers-json');

  // Preconditions
  console.assert(tableBody, '#teachers-table-body is required');
  console.assert(jsonOutput, '#teachers-json is required');

  async function loadTeachers() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/timetable/teachers/`);
      if (!res.ok) throw new Error('Failed to fetch teachers');
      const teachers = await res.json();

      // Postconditions
      console.assert(Array.isArray(teachers), 'Expected teachers to be an array');
      console.assert(teachers.every(t => 'id' in t && 'name' in t), 'Each teacher must have id and name');

      // Render table
      tableBody.innerHTML = '';
      teachers.forEach(teacher => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${teacher.id}</td>
          <td>${teacher.name}</td>
        `;
        tableBody.appendChild(row);
      });

      // Invariant
      console.assert(tableBody.children.length === teachers.length, 'Mismatch between table rows and teachers data');

      jsonOutput.textContent = JSON.stringify(teachers, null, 2);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="2">Error loading teachers</td></tr>`;
      jsonOutput.textContent = err.message;

      console.assert(tableBody.innerHTML.includes('Error'), 'Error row not rendered properly');
    }
  }
  loadTeachers();
});
