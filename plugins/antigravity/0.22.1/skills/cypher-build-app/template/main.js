// PURPOSE
// -------
// Wires up index.html's cu-* elements. Only touches the kit's own
// elements and the events/attributes their docs define — no raw DOM
// elements are created here.
//
// AGENT NOTES
// -----------
// - `cu-click` below is illustrative. Confirm the real event name this
//   kit version fires for `cu-button` against `custom-elements.json`
//   (from `knowledge {topic: "cypherui"}`) before relying on it.

const byId = (id) => document.getElementById(id);

const greetButton = byId("greet");
const greeting = byId("greeting");

greetButton.addEventListener("cu-click", () => {
  greeting.hidden = false;
});
