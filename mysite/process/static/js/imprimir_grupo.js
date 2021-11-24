function generar_reporte_grupo(){
    var element = document.getElementById('imprimir_grupo_estadistica');
    html2pdf().set({
        margin:1,
        html2canvas:{
            scale:3,
            letterRendering: true,
        },
        jsPDF :{
            unit:"in" ,
            format:"a3",
            orientation:'portrait'
        }
    })
    .from(element).save();
};