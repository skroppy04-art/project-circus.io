export async function onRequest(context) {

  const response = await fetch(
    "http://213.171.18.141:32946/v1/server",
    {
      headers: {
        "x-auth-key": "Project_Circus_API_Seckret"
      }
    }
  );

  const data = await response.json();

  return new Response(JSON.stringify(data), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
