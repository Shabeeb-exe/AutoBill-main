var InitialCount = -1;



const deleteProducts = async() => {
    url = 'https://autobill-main-8knj.onrender.com/product';

    let res = await axios.get(url);
    responseText = res.data;
    const products = responseText;

    for (let product of products) {
        const response = await axios.delete(`https://autobill-main-8knj.onrender.com/product/${product.id}`)

    }
    location.reload();
    window.scroll({
        top: 0,
        left: 0,
        behavior: 'smooth'
    });
}

const loadProducts = async() => {
    url = 'https://autobill-main-8knj.onrender.com/product';

    let res = await axios.get(url);
    responseText = await res.data;
    const products = responseText;
    var len = products.length;

    if (len > InitialCount + 1) {
        $("#1").css("display", "none");
        $("#home").css("display", "grid");
        $("#2").css("display", "grid");
        var payable = 0;
        const products = responseText;
        console.log(products);
        for (let product of products) {
            payable = payable + parseFloat(product.payable);

        }

        var product = products.pop();
        const x = `
        <section>
                <div class="card card-long animated fadeInUp once">
                    <img src="asset/img/${product.name}.jpg" class="album">
                    <div class="span1">Product Name</div>
                    <div class="card__product">
                        <span>${product.name}</span>
                    </div>
                    <div class="span2">Per Unit</div>
                    <div class="card__price">
                        <span>${product.price} </span>
                    </div>
                    <div class="span3">Units</div>
                    <div class="card__unit">
                        <span>${product.taken} ${product.units}</span>
                    </div>

                    <div class="span4">Payable</div>
                    <div class="card__amount">
                        <span>${product.payable}</span>
                    </div>
                </div>
            </section>
        <section>
        `

        document.getElementById('home').innerHTML = document.getElementById('home').innerHTML + x;
        document.getElementById('2').innerHTML = "CHECKOUT ₹" + payable;
        InitialCount += 1;
    }


}

var checkout = async() => {
    document.getElementById('2').innerHTML = "<span class='loader-16' style='margin-left: 44%;'></span>"
    var payable = 0;
    url = 'https://autobill-main-8knj.onrender.com/product';

    let res = await axios.get(url);
    responseText = await res.data;
    products = responseText;

    for (let product of products) {
        payable = payable + parseFloat(product.payable);
    }

    var url = "https://upiqr.in/api/qr?name=Rayan&vpa=8113955334@ibl";

    await fetch(url)
        .then(function(data) {
            return data.blob();
        })
        .then(function(img) {
            var image = URL.createObjectURL(img);
            $("#home").css("display", "none");
            $("#final").css("display", "none");
            window.scroll({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });
            $('#image').attr('src', image);
            $("#qr").css("display", "grid");

        });
    setTimeout(function(){
        $("#qr").css("display", "none");
        $("#success").css("display", "grid");
            },10000);
        

    // window.location.href = "upi://pay?pa=shebinjosejacob2014@oksbi&pn=TXN9656549238&tn=A&am=1&cu=INR&url=https://assettracker.cf/"*/
    deleteProducts();
}
