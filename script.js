document.getElementById('add_intervention').addEventListener('click', function() {
    var customInterventionValue = document.getElementById('custom_intervention').value.trim();
    if (customInterventionValue) {
        createCheckbox('.form-group.interventions', 'intervention', customInterventionValue);
        document.getElementById('custom_intervention').value = '';
    }
});

document.getElementById('add_constraint').addEventListener('click', function() {
    var customConstraintValue = document.getElementById('custom_constraint').value.trim();
    if (customConstraintValue) {
        createCheckbox('.form-group.constraints', 'constraint', customConstraintValue);
        document.getElementById('custom_constraint').value = '';
    }
});

function createCheckbox(targetClass, name, value) {
    var div = document.createElement('div');
    div.className = 'checkbox-group';
    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.name = name;
    checkbox.value = value;
    var label = document.createElement('label');
    label.textContent = value;

    div.appendChild(checkbox);
    div.appendChild(label);
    document.querySelector(targetClass).appendChild(div);
}