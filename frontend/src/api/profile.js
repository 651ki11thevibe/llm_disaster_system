// src/api/profile.js
import axios from "axios";

const BASE_URL = "http://localhost:8080";

export function getProfile(token) {
  return axios.get(`${BASE_URL}/user/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function updateUserId(token, data) {
  return axios.post(`${BASE_URL}/user/update_user_id`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function changePassword(token, data) {
  return axios.post(`${BASE_URL}/user/change_password`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}
