
document.getElementById('add_intervention').addEventListener('click', function() {
    var customInterventionValue = document.getElementById('custom_intervention').value.trim();
    if (customInterventionValue) {
        createCheckbox('.interventions', 'intervention', customInterventionValue); // Ensure correct targeting
        document.getElementById('custom_intervention').value = '';
    }
});

document.getElementById('add_constraint').addEventListener('click', function() {
    var customConstraintValue = document.getElementById('custom_constraint').value.trim();
    if (customConstraintValue) {
        createCheckbox('.constraints', 'constraint', customConstraintValue); // Ensure correct targeting
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
const admin = require('firebase-admin');
const serviceAccount = require('.//Users/hiwotbelaytadesse/Downloads/db-for-wearables-project-firebase-adminsdk-wffpb-853b04724d.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function fetchData() {
  const snapshot = await db.collection('Test1').get();
  snapshot.forEach(doc => {
    console.log(doc.id, '=>', doc.data());
  });
}

fetchData();