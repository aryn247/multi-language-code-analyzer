function greet(name) {
    console.log("Hello, " + name);
}

function add(a, b) {
    return a + b;
}

function nestedLoop(n) {
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            console.log(i * j);
        }
    }
}

greet("Aryan");
