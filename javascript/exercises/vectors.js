var i_hat = "\\hat{i}";
var j_hat = "\\hat{j}";

function addVectors(v1, v2) {
    return {x: v1.x + v2.x, y: v1.y + vy.y};
}

function indexOf(vectors, v) {
    for(var i = 0; i < vectors.length; i++) {
        if (are_equal_vectors(v, vectors[i]))
            return i;
    }
    return -1;
}

function are_equal_vectors(vector, other) {
    return vector.x == other.x && vector.y == other.y;
}

function isOutOfBounds(vector) {
    return vector.x >=10 || vector.x <= -10 || vector.y >= 10 || vector.y <= -10;
}

function outputVector(v) {
    var i = format_first_coefficient(v.x);
    var j = format_coefficient(v.y);
    if (v.x) {
        i += i_hat;
        j = format_coefficient(v.y);
    } else {
        i = "";
        j = format_first_coefficient(v.y);
    }
        
    if (v.y)
        j += j_hat;
    else
        j = "";            
        
    if (!i && !j)
        j = "0";

    return i + j;
}

function outputColorTag(color) {
    return "<span style='color: " + color + "'>";
}