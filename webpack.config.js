// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAWHRTXBk5iOkL9jIKqGG1aJekR3g2t-9w",
  authDomain: "db-for-wearables-project.firebaseapp.com",
  projectId: "db-for-wearables-project",
  storageBucket: "db-for-wearables-project.appspot.com",
  messagingSenderId: "338661746993",
  appId: "1:338661746993:web:8fc31eae7e09651892a810",
  measurementId: "G-N425ZDH3VM"
};


async function fetchData() {
  const snapshot = await db.collection('yourCollection').get();
  snapshot.forEach(doc => {
    console.log(doc.id, '=>', doc.data());
  });
}


fetchData();


// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
import { getFirestore, collection, getDocs } from "firebase/firestore";

const db = getFirestore();

async function displayEntries() {
  const querySnapshot = await getDocs(collection(db, "yourCollectionName"));
  querySnapshot.forEach((doc) => {
    console.log(`${doc.id} => ${JSON.stringify(doc.data())}`);
    // Append data to your webpage here
  });
}

displayEntries();
