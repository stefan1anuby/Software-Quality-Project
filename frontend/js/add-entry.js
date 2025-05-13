// Handle form submission to create a new schedule entry
const API_BASE = 'http://localhost:8000';

document.getElementById('entry-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  // TODO: collect actual field values
  const form = e.target;
  const data = {
    day_of_week: form.elements['day_of_week'].value,
    start_hour: form.elements['start_hour'].value,
    end_hour: form.elements['end_hour'].value,
    teacher_id: form.elements['teacher_id'].value,
    room_id: form.elements['room_id'].value,
    subject_id: form.elements['subject_id'].value,
    letter: form.elements['letter'].value,
    class_type: form.elements['class_type'].value,
  };

  try {
      const res = await fetch(`${API_BASE}/api/v1/timetable/schedule/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    alert('Entry added successfully');
    e.target.reset();
  } catch (err) {
    alert('Error: ' + err.message);
  }
});