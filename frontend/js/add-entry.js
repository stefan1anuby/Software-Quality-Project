// Handle form submission to create a new schedule entry
const API_BASE = 'http://localhost:8000';

document.getElementById('entry-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  // TODO: collect actual field values
  const data = {
    day_of_week: e.target.day_of_week.value,
    start_hour: parseInt(e.target.start_hour.value),
    end_hour: parseInt(e.target.end_hour.value),
    teacher_id: parseInt(e.target.teacher_id.value),
    room_id: parseInt(e.target.room_id.value),
    subject_id: parseInt(e.target.subject_id.value),
    class_type: e.target.class_type.value,
    student_group_id: e.target.student_group_id.value || null,
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