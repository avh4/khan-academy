// Arithmetic Word Problmes Author: Rock Hymas
//
// Problem spec: http://www.youtube.com/watch?v=Ff_cjv5KUs4
//
// Problem layout: You are given one of three types of problems.  You have to determine
// how the problem is expressed in terms of multiplication/division/addition/subtraction 
// and work out the answer.
//

function ArithmeticWordProblemsExercise() {
    gender = {
        male: { pronoun: "he", cpronoun: "He" },
        female: { pronoun: "she", cpronoun: "She" }
    };
    people = [
        { name: 'Alice', gender: 'female' },
        { name: 'Bob', gender: 'male' },
        { name: 'Charlie', gender: 'male' },
        { name: 'Dane', gender: 'male' },
        { name: 'Eve', gender: 'female' },
        { name: 'Frank', gender: 'male' },
        { name: 'Gary', gender: 'male' },
        { name: 'Helen', gender: 'female' },
        { name: 'Ira', gender: 'male' },
        { name: 'Jennifer', gender: 'female' },
        { name: 'Karl', gender: 'male' },
        { name: 'Lily', gender: 'female' },
        { name: 'Mario', gender: 'male' },
        { name: 'Nina', gender: 'female' },
        { name: 'Oscar', gender: 'male' }
    ];
    collections = [
        { object: {i:'chair', is:'chairs'}, collection: {i:'row', is:'rows' } },
        { object: {i:'party favor', is:'party favors'}, collection: {i:'bag', is:'bags' } },
        { object: {i:'jelly bean', is:'jelly beans'}, collection: {i:'pile', is:'piles' } },
        { object: {i:'book', is:'books'}, collection: {i:'shelf', is:'shelves' } },
        { object: {i:'can of food', is:'cans of food'}, collection: {i:'box', is:'boxes' } }
    ];
    stores = [
        { name: 'office supply', items: [ {i:'pen', is:'pens'}, {i:'pencil', is:'pencils'}, {i:'notebook', is:'notebooks'}] },
        { name: 'hardware', items: [ {i:'hammer', is:'hammers'}, {i:'nail', is:'nails'}, {i:'saw', is:'saws'}] },
        { name: 'grocery', items: [ {i:'banana', is:'bananas'}, {i:'loaf of bread', is:'loaves of bread'}, {i:'gallon of milk', is:'gallons of milk'}, {i:'potato', is:'potatoes'}] },
        { name: 'gift', items: [ {i:'toy', is:'toys'}, {i:'game', is:'games'}, {i:'souvenirs', is:'souvenirs'}] },
        { name: 'toy', items: [ {i:'stuffed animal', is:'stuffed animals'}, {i:'video game', is:'video games'}, {i:'race car', is:'race cars'}, {i: 'doll', is:'dolls'}] }
    ];

    swap = function(arr, i1, i2) {
        var temp = arr[i1];
        arr[i1] = arr[i2];
        arr[i2] = temp;
    };

    factorpairs = function(val) {
        var result = new Array();
        var x = 0;
        for (x = 2; x <= Math.sqrt(val); x++) {
            if (val % x == 0) {
                var len = result.push([x, val / x]);
                if (getRandomIntRange(0, 1) == 1) { // sometimes swap
                    swap(result[len - 1], 0, 1);
                }
            }
        }
        // Now mix it up
        var i = result.length;
        if (i < 2) return result;
        while (--i) {
            var j = getRandomIntRange(0, i);
            swap(result, i, j);
        }
        return result;
    };

    this.person = null;
    this.item1 = null;
    this.item2 = null;
    this.fps = null;
    this.total = 0;
    this.store = null;

    this.replace = function(string_in){
        var str = string_in;
        str = str.replace(/\@n/g, this.person.name);
        str = str.replace(/\@p/g, gender[this.person.gender].pronoun);
        str = str.replace(/\@P/g, gender[this.person.gender].cpronoun);
        str = str.replace(/\@s/g, this.store);
        str = str.replace(/\@0/g, this.fps[0][0]);
        str = str.replace(/\@1/g, this.fps[0][1]);
        str = str.replace(/\@2/g, this.fps[1][0]);
        str = str.replace(/\@3/g, this.fps[1][1]);
        str = str.replace(/\@x/g, this.fps[1][0] * this.fps[1][1]);
        str = str.replace(/\@e/g, this.total - (this.fps[1][0] * this.fps[1][1]));
        str = str.replace(/\@t/g, this.total);
        str = str.replace(/ 1 \@o1s/g, ' 1 ' + this.item1.i);
        str = str.replace(/ 1 \@o2s/g, ' 1 ' + this.item2.i);
        str = str.replace(/\@o1s/g, this.item1.is);
        str = str.replace(/\@o2s/g, this.item2.is);
        str = str.replace(/\@o1/g, this.item1.i);
        str = str.replace(/\@o2/g, this.item2.i);
        return str;
    };

    this.type1 = function() {
        do {
            this.total = nonZeroRandomInt(10, 99);
            this.fps = factorpairs(this.total)
        } while (this.fps.length < 2); // wait till we get one with enough factors

        setCorrectAnswer(this.fps[1][1]);

        writeText(this.replace("When @n places @0 @o1s in each @o2 @p ends up with @1 @o2s. If @p wants @2 @o2s, how many @o1s should @p put in each @o2?"));
        writeStep(this.replace("<li>@0 @o1s `\\times` @1 @o2s = @x @o1s</li>"));
        writeStep(this.replace("<li>If we divide the @x @o1s into @2 @o2s then we get `@x \\divide @2 = @3` @o1s per @o2.</li>"));
    };

    this.type2 = function() {
        var store = randomMember(stores);
        this.store = store.name;
        this.item1 = randomMember(store.items);
        do { this.item2 = randomMember(store.items); } while (this.item2 == this.item1);

        do {
            this.total = nonZeroRandomInt(10, 99);
            this.fps = factorpairs(this.total);
        } while (this.fps.length < 2); // wait till we get one with enough factors

        var extra = nonZeroRandomInt(1,50);
        this.total = this.total + extra;

        setCorrectAnswer(this.fps[0][1]);

        writeText(this.replace("@n bought @0 @o1s, all costing the same amount, from the @s store. @P also bought a @o2 for @e dollars. @P spent a total of @t dollars. How much did each @o1 cost?"));
        writeStep(this.replace("<li>Of the @t dollars, @p spent @e dollars on a @o2 so @p must have spent `@t - @e = @x` dollars on @o1s.</li>"));
        writeStep(this.replace("<li>@P spent @x dollars on @0 @o1s, so @p must have spent `@x \\divide @0 = @1` dollars on each @o1.</li>"));
    };

    this.type3 = function() {
        do {
            this.total = nonZeroRandomInt(10, 99);
            this.fps = factorpairs(this.total);
        } while (this.fps.length < 1); // wait till we get one with enough factors

        var extra = nonZeroRandomInt(1,10);
        while (this.total % extra == 0) {
            extra = nonZeroRandomInt(1,10);
        }
        this.fps[1] = [extra, Math.floor(this.total / extra)];

        setCorrectAnswer(this.fps[0][1]);

        writeText(this.replace("@n is putting @o1s into @o2s. If @p puts @2 @o1s in each @o2 @p will make @3 @o2s and have @e @o1s left over. If @p instead puts @0 @o1s in each @o2, how many @o2s of @o1s can @p make?"));
        writeStep(this.replace("<li>@3 @o2s of @2 @o1s each results in `@3 \\times @2 = @x` @o1s</li>"));
        writeStep(this.replace("<li>@x @o1s plus @e left over equals @t total @o1s.</li>"));
        writeStep(this.replace("<li>@t @o1s divided into groups of @0 is `@t \\divide @0 = @1` @o2s</li>"));
    };

    this.init = function() {
        this.total = 0;
        this.fps = new Array();

        this.person = randomMember(people);
        var col = randomMember(collections);
        this.item1 = col.object;
        this.item2 = col.collection;

        var type = getRandomIntRange(1,3);
        this['type' + type]();
    };
}
