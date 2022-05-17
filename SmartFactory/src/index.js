/** @odoo-module **/

// import core from 'web.core';
import {registry} from '@web/core/registry'
import superagent from 'superagent';

const {Component, useState} = owl;
console.log(owl);

var piwebapiURL = "https://prod400azdb02.svcs.itesm.mx/piwebapi/";

// function updateCharge(response) {
//     this.battery1 = response.json().Value;
// }
//
// function fetchCharge(){
//     var request = new XMLHttpRequest();
//     request.addEventListener("load", updateCharge.bind(this));
//     request.setRequestHeader('Authorization', '');
//     request.open("GET", piwebapiURL + "streams/F1DPAVp1V4jMukCbSUCQw1guxAuAIAAAUFJPRDQwMEFaREIwMlxCQVRURVJZ/end");
//     request.send();
// }
// function init() {
//     this.fetchInterval = setInterval(fetchCharge.bind(this), 2000);
// }
//
// function destroy() {
//     clearInterval(this.fetchInterval);
// }
//
// var action = {
//     hasControlPanel: true,
//     template: 'SmartFactory.main',
//     battery1: 100,
//     init: init.bind(this),
//     destroy: destroy.bind(this),
// }

class SmartFactoryIndex extends Component {
    state = useState({
        battery1: 0,
    })

    setup() {
    }

    willStart() {
        this.timeout = setTimeout(this.handleTimeout, 1000);
    }

    onWillDestroy() {
        clearTimeout(this.timeout);
    }

    handleResponse(err, res) {
        this.state.battery1 = res.body.Value;
    }

    handleTimeout() {
        superagent
            .get(piwebapiURL + "streams/F0DPAVp1V4jMukCbSUCQw1guxAuAIAAAUFJPRDQwMEFaREIwMlxCQVRURVJZ/end")
            .set('Authentication', 'Basic VEVDXHQtZXJpay4vbHZlcmE6KkVTT01zaW9zMDE=')
            .set('accept', 'json')
            .end(this.handleRequest);
    }
}

SmartFactoryIndex.template = 'SmartFactory.main';

registry.category('actions').add('smart-factory-window', SmartFactoryIndex);