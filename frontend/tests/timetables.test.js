import { jest } from '@jest/globals';
import * as module from '../js/timetables.js';

beforeEach(() => {
  document.body.innerHTML = `
    <select id="group-select">
      <option value="A">Group A</option>
      <option value="B">Group B</option>
    </select>
    <table><tbody id="timetable-body"></tbody></table>
    <pre id="timetable-raw"></pre>
  `;
});

global.fetch = jest.fn();
global.confirm = jest.fn();
global.alert = jest.fn();

const mockData = [
  {
    id: 1,
    day_of_week: 'Monday',
    start_hour: 10,
    end_hour: 12,
    subject_id: 1,
    room_id: 101,
    teacher_id: 5,
    student_group_id: 'A'
  }
];

describe('Timetables Page', () => {
  beforeEach(async () => {
    jest.resetModules();
    fetch.mockClear();
  });

  test('loads and displays timetable correctly', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    const module = await import('../js/timetables.js');
    await module.loadTimetable();

    expect(fetch).toHaveBeenCalled();
    expect(document.getElementById('timetable-body').innerHTML).toContain('Monday');
    expect(document.getElementById('timetable-raw').textContent).toContain('Monday');
  });

  test('displays message when no timetable available', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    const module = await import('../js/timetables.js');
    await module.loadTimetable();

    expect(document.getElementById('timetable-body').innerHTML).toContain('No timetable available');
  });

  test('handles fetch error gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));
    const module = await import('../js/timetables.js');
    await module.loadTimetable();

    expect(document.getElementById('timetable-raw').textContent).toContain('Error: Network error');
  });

  test('deletes entry after confirmation', async () => {
    fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockData })
      .mockResolvedValueOnce({ status: 204 });

    confirm.mockReturnValueOnce(true);

    const module = await import('../js/timetables.js');
    await module.deleteEntry(1);

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/timetable/schedule/1',
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  test('cancels deletion when confirm returns false', async () => {
    confirm.mockReturnValueOnce(false);
    const module = await import('../js/timetables.js');
    await module.deleteEntry(2);

    expect(fetch).not.toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/timetable/schedule/2',
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});
