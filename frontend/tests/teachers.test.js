/**
 * @jest-environment jsdom
 */

const mockTeachers = [
  { id: 1, name: 'Jane Doe' },
  { id: 2, name: 'John Smith' },
];

beforeEach(() => {
  document.body.innerHTML = `
    <table>
      <tbody id="teachers-table-body"></tbody>
    </table>
    <pre id="teachers-json"></pre>
    <form id="teacher-form">
      <input id="teacher-name" />
    </form>
  `;

  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockTeachers),
    })
  );
});

afterEach(() => {
  jest.resetModules();
  jest.clearAllMocks();
});

test('loads and displays teachers in table and JSON', async () => {
  await import('../js/teachers.js');

  document.dispatchEvent(new Event('DOMContentLoaded'));
  await new Promise(resolve => setTimeout(resolve, 0));;

  const rows = document.querySelectorAll('#teachers-table-body tr');
  expect(rows.length).toBe(2);
  expect(rows[0].innerHTML).toContain('Jane Doe');
  expect(rows[1].innerHTML).toContain('John Smith');

  const jsonOutput = document.getElementById('teachers-json').textContent;
  expect(jsonOutput).toContain('"name": "Jane Doe"');
  expect(jsonOutput).toContain('"name": "John Smith"');

  expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/timetable/teachers/');
});

test('displays error message when fetch fails', async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: false,
    })
  );

  await import('../js/teachers.js');
  document.dispatchEvent(new Event('DOMContentLoaded'));
  await new Promise(resolve => setTimeout(resolve, 0));;

  const errorRow = document.querySelector('#teachers-table-body tr');
  expect(errorRow).not.toBeNull();
  expect(errorRow.innerHTML).toContain('Error loading teachers');

  const jsonOutput = document.getElementById('teachers-json').textContent;
  expect(jsonOutput).toBe('Failed to fetch teachers');
});

test('clears table before rendering new data', async () => {
  document.getElementById('teachers-table-body').innerHTML = `
    <tr><td>Old</td><td>Data</td></tr>
  `;

  await import('../js/teachers.js');
  document.dispatchEvent(new Event('DOMContentLoaded'));
  await new Promise(resolve => setTimeout(resolve, 0));;

  const rows = document.querySelectorAll('#teachers-table-body tr');
  expect(rows.length).toBe(2);
  expect(rows[0].innerHTML).toContain('Jane Doe');
  expect(rows[1].innerHTML).toContain('John Smith');
});

test('renders well-formatted JSON', async () => {
  await import('../js/teachers.js');
  document.dispatchEvent(new Event('DOMContentLoaded'));
  await new Promise(resolve => setTimeout(resolve, 0));;

  const jsonText = document.getElementById('teachers-json').textContent;

  expect(jsonText).toMatch(/\{\n\s+"id": 1,/);
  expect(jsonText).toMatch(/"name": "Jane Doe"/);
});
