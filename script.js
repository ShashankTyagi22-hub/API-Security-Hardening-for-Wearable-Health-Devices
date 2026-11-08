const heartRate=document.getElementById("heartRate");
const temperature=document.getElementById("temperature");
const steps=document.getElementById("steps");
const attacks=document.getElementById("attacks");

const apiFill=document.getElementById("apiFill");

let requestCount=0;

function randomHealthData(){

let hr=Math.floor(Math.random()*40)+70;

let temp=(36+Math.random()).toFixed(1);

let step=Math.floor(Math.random()*12000);

heartRate.innerText=hr+" BPM";

temperature.innerText=temp+"°C";

steps.innerText=step;

}

setInterval(randomHealthData,3000);

function updateRequests(){

requestCount+=Math.floor(Math.random()*8);

if(requestCount>100)
{
    requestCount=0;
}

apiFill.style.width=requestCount+"%";

}

setInterval(updateRequests,2000);

function addSecurityLog(message,type){

const logs=document.getElementById("logs");

const div=document.createElement("div");

div.classList.add("log");
div.classList.add(type);

div.innerText=message;

logs.prepend(div);

if(logs.children.length>10)
{
logs.removeChild(logs.lastChild);
}

}

setInterval(()=>{

const messages=[

{
msg:"JWT Authentication Successful",
type:"success"
},

{
msg:"Rate Limit Triggered",
type:"warning"
},

{
msg:"Unauthorized API Attempt Blocked",
type:"danger"
},

{
msg:"Encrypted Health Data Stored",
type:"success"
},

{
msg:"Suspicious Device Rejected",
type:"danger"
}

];

const random=
messages[
Math.floor(
Math.random()*messages.length
)
];

addSecurityLog(
random.msg,
random.type
);

},4000);

function attackCounter(){

let current=
parseInt(attacks.innerText);

current+=Math.floor(Math.random()*2);

attacks.innerText=current;

}

setInterval(
attackCounter,
7000
);

fetch("http://127.0.0.1:5000/api/data")
.then(response=>response.json())
.then(data=>{

console.log(data);

})
.catch(error=>{

console.log(error);

});

function showPage(pageId)
{
    let pages =
    document.querySelectorAll(".page");

    pages.forEach(page =>
    {
        page.style.display = "none";
    });

    document.getElementById(pageId)
    .style.display = "block";
}

function showPage(pageId)
{
    const pages =
    document.querySelectorAll(".page");

    pages.forEach(page =>
    {
        page.style.display = "none";
    });

    document.getElementById(pageId)
    .style.display = "block";
}