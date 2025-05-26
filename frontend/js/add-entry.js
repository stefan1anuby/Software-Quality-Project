// Handle form submission to create a new schedule entry
const API_BASE = 'http://localhost:8000';

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

document.getElementById('entry-form').addEventListener('submit', async (e) => {
  e.preventDefault();

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

  // Assert each required field has a value
  try {
    assert(data.day_of_week, 'Day of week is required');
    assert(data.start_hour, 'Start hour is required');
    assert(data.end_hour, 'End hour is required');
    assert(data.teacher_id, 'Teacher ID is required');
    assert(data.room_id, 'Room ID is required');
    assert(data.subject_id, 'Subject ID is required');
    assert(data.letter, 'Letter is required');
    assert(data.class_type, 'Class type is required');

    // You could also add specific format checks, e.g.:
    assert(/^\d{2}:\d{2}$/.test(data.start_hour), 'Start hour format must be HH:MM');
    assert(/^\d{2}:\d{2}$/.test(data.end_hour), 'End hour format must be HH:MM');

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
