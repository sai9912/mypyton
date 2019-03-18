import Vue from 'vue';
import _ from 'lodash';

Vue.config.productionTip = false

let editContext = require.context('./productedit/specs/', true, /\.spec$/);
editContext.keys().forEach(editContext)

let createContext = require.context('./productcreate/specs/', true, /\.spec$/);
createContext.keys().forEach(createContext)

//const srcContext = require.context('../src/productedit', true, /^\.\/(?!index(\.js)?$)/)
//srcContext.keys().forEach(srcContext)
