/**
 * @jest-environment jsdom
 */

import fs from 'fs';
import path from 'path';
import { fireEvent } from '@testing-library/dom';

global.fetch = jest.fn();

beforeEach(() => {
  document.body.innerHTML = fs.readFileSync(
    path.resolve(__dirname, '../create-schedule.html'),
    'utf8'
  );

  jest.resetModules();
  require('../js/add-entry.js');
});

afterEach(() => {
  fetch.mockClear();
});

function fillForm(valid = true) {
  document.querySelector('[name="day_of_week"]').value = valid ? 'Monday' : '';
  document.querySelector('[name="start_hour"]').value = valid ? '9' : '';
  document.querySelector('[name="end_hour"]').value = valid ? '10' : '';
  document.querySelector('#teacher-select').value = valid ? '1' : '';
  document.querySelector('#room-select').value = valid ? '1' : '';
  document.querySelector('#subject-select').value = valid ? '1' : '';
  document.querySelector('[name="class_type"]').value = valid ? 'Lecture' : '';
  document.querySelector('#group-select').value = valid ? '2' : '';
}

test('should submit form with valid input and reset form', async () => {
  const form = document.getElementById('entry-form');
  const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

  fillForm(true);

  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ success: true }),
  });

  fireEvent.submit(form);

  await new Promise((r) => setTimeout(r, 0));

  expect(fetch).toHaveBeenCalledWith(
    expect.stringContaining('/schedule/'),
    expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
  );

  expect(alertMock).toHaveBeenCalledWith('Entry added successfully');
  alertMock.mockRestore();
});

test('should show error alert if API submission fails', async () => {
  const form = document.getElementById('entry-form');
  const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

  fillForm(true);

  fetch.mockResolvedValueOnce({
    ok: false,
    json: async () => ({ detail: 'Invalid data' }),
  });

  fireEvent.submit(form);
  await new Promise((r) => setTimeout(r, 0));

  expect(alertMock).toHaveBeenCalledWith(expect.stringContaining('Error: Invalid data'));
  alertMock.mockRestore();
});

test('should not submit form if fields are missing', () => {
  const form = document.getElementById('entry-form');
  const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

  fillForm(false); // Fill with empty/invalid values

  fireEvent.submit(form);

  expect(fetch).not.toHaveBeenCalled();
  expect(alertMock).toHaveBeenCalled();
  alertMock.mockRestore();
});
