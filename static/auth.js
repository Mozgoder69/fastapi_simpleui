// auth.js

document.addEventListener("DOMContentLoaded", async function () {
  try {
    const response = await ky.get(`${window.apiUrl}/api/auth`).json();
    if (!response.user) throw new Error("Unauthorized Access");
    console.log("Auth Passed");
    toast("Auth Passed");
  } catch (error) {
    console.error("Auth Failed by: ", error);
    toast("Auth Failed");
    document.location.href = "/login";
  }
});
