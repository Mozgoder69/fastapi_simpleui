// alpaca-setup.js

$(document).ready(function () {
  // inject with jinja2
  const schema = "{{ schema|tojson }}";
  const table = "{{ table|safe }}";
  if (!schema || !table) {
    console.error("Schema or table is undefined.");
    return;
  }
  $("#form").alpaca({ schema, options: getFormOptions(schema, table) });
});

function getFormOptions(schema, table) {
  return {
    fields: {
      feedback: {
        type: "textarea",
        helper: "Feedback",
        fieldClass: "materialize-textarea",
        onFieldRendered: function (control) {
          applyAlpineDirectives(control);
        },
      },
      ranking: {
        type: "radio",
        helper: "Ranking",
        fieldClass: "with-gap",
        vertical: true,
      },
    },
    form: { attributes: { class: "col s12" } },
    postRender: applyStylesToForms,
  };
}

function applyAlpineDirectives(control) {
  control.getFieldEl().setAttribute("x-data", '{ name: "" }');
  control.getFieldEl().querySelector("input").setAttribute("x-model", "name");
  control
    .getFieldEl()
    .querySelector("label")
    .setAttribute("x-bind:class", "{ active: name }");
}
