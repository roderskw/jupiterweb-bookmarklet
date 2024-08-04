javascript: (function () {

    function ensure_url(url) {
        if (location.href != url) {
            alert(
                "Este script deve ser rodado na página de grade horária!\n\n" +
                "Você será redirecionado para lá. Rode de novo quando abrir a grade..."
            );
            location.assign(url);
            return false;
        }
        return true;
    }

    function find_table() {
        ensure_url("https://uspdigital.usp.br/jupiterweb/gradeHoraria?codmnu=4759");
        const grade = document.getElementById("gbox_tableGradeHoraria");
        if(!grade)
            alert("Não foi encontrado uma grade horária aberta!");
        return grade; 
    }

    function inner(elem, arr) { 
        for (const i of arr)   
            elem = elem.children[i];
        return elem; 
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function get_table_lines() {
       const table =  inner(find_table(), [2, 2, 0, 1, 0]);
       return Array.from(table.childNodes).slice(1);
    }

    function find_oferecimento_button() {
        const details = inner(document.getElementById("tab_detalhes"), [0, 1, 0]);
        if(document.getElementById("div_detalhes").getAttribute("style").includes("none"))
            return null;
        return details;
    }

    function get_name() {
        return  document.getElementsByClassName("nomdis")[1].innerText;
    }

    function check_offer() {
        if(document.getElementById("div_detalhes").getAttribute("style").includes("none")) {
            console.log("Os detalhes nao estao abertos!");
            return null;
        }
        if(document.getElementById("div_oferecimento").getAttribute("class").includes("hide")) {
            console.log("O oferecimento nao esta aberto!");
            return null;
        }
        return document.getElementsByClassName("adicionado").item(0);
    }

    function get_info() {
        const tables = check_offer();
        if(!tables) return null;

        var info = [];
        var info_lines = Array.from(inner(tables, [1, 0]).children).slice(0, -2);

        info.push(info_lines[1].children[1].innerText.replace('\t',' '));
        info.push(info_lines[2].children[1].innerText.replace('\t',' '));

        return info;
    }

    function get_days() {
        const tables = check_offer();
        if(!tables) return null;

        var days = [];
        var days_lines = Array.from(inner(tables, [2, 1]).children);

        for(let i = 0; i < days_lines.length; i++)
            days.push(Array.from(days_lines[i].children).pop().innerText);

        const s = new Set(days);
        return Array.from(s).toString();
    }


    async function get_data() {
        const elem = get_table_lines();
        var codes = [];
        var classes = [];
        for (const tr of elem) { 
            var start = tr.children[0].innerText;
            var end = tr.children[1].innerText; 

            for(let i = 2; i < tr.children.length; i++) {
                var txt = tr.children[i].innerText;
                if(txt) {
                    if(!codes.includes(txt)) {
                        codes.push(txt);
                        var botao = tr.children[i].children[0];
                        botao.click();
                        await sleep(700);
                        find_oferecimento_button().click();
                        await sleep(700);
                        const info =  get_info();
                        classes.push({weekday : i - 2, code : txt, name : get_name(), start : start, end : end, 
                        start_date : info[0], end_date : info[1], prof : get_days()});
                    }
                    else {
                        for(let j = 0; j < classes.length; j++) {
                            if(classes[j].code == txt) {
                                let c = JSON.parse(JSON.stringify(classes[j]));
                                c.weekday = i - 2;
                                c.start = start;
                                c.end = end;
                                classes.push(c);
                                break;
                            }
                        }
                    }
                }
            }
            
        }

        return classes; 
    }

    function download(filename, text) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
      
        element.style.display = 'none';
        document.body.appendChild(element);
      
        element.click();
      
        document.body.removeChild(element);
    }

    async function go() {
        const data = await get_data();
        download("grade.txt", JSON.stringify(data));
    }

    go();

})()

