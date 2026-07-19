// Welcome Message
console.log("Welcome to SRI MAHA REAL ESTATE");

// Highlight Active Menu
const links = document.querySelectorAll("nav a");

links.forEach(link => {
    if (link.href === window.location.href) {
        link.style.color = "yellow";
    }
});

// Explore Button Animation
const btn = document.querySelector(".btn");

if (btn) {
    btn.addEventListener("mouseover", function () {
        btn.style.transform = "scale(1.05)";
        btn.style.transition = "0.3s";
    });

    btn.addEventListener("mouseout", function () {
        btn.style.transform = "scale(1)";
    });
}