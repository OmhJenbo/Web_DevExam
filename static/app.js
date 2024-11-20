function render_items(data){
    data = JSON.parse(data)
    data.forEach(e=>{
        console.log(e)
        var marker = L.marker(e.coords).addTo(map)
        marker.bindPopup(e.popup)
    })

}