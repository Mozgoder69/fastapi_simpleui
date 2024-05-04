// fetch_ky-setup.js

async function fetchRequest(url, options) {
  try {
    const response = await ky(url, options).json();
    toast("Success");
    return response;
  } catch (error) {
    console.error("Error:", error);
    toast("Error: " + error.message);
    throw error;
  }
}

async function read_one(table, oid) {
  return await fetchRequest(`${window.apiUrl}/${table}/${oid}`, {
    method: "GET",
  });
}

async function list_many(table) {
  return await fetchRequest(`${window.apiUrl}/${table}/list`, {
    method: "GET",
  });
}

async function new_one(table, data) {
  return await fetchRequest(`${window.apiUrl}/${table}/new`, {
    method: "POST",
    json: data,
  });
}

async function edit_one(table, oid, data) {
  return await fetchRequest(`${window.apiUrl}/${table}/${oid}`, {
    method: "PUT",
    json: data,
  });
}

async function trim_many(table, oids) {
  return await fetchRequest(`${window.apiUrl}/${table}/bulk`, {
    method: "DELETE",
  });
}
