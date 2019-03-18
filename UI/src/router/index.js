import Router from 'vue-router'
import Layout from './../components/Layout/Layout'
import AppWait from '../components/AppWait/AppWait'
import Dashboard from './../components/Dashboard/Dashboard'
import Prefixes from './../components/Prefixes/Prefixes'
import ListProducts from './../components/Products/ListProducts/ListProducts'
import AddProduct from './../components/Products/AddProduct/AddProduct'
import ExportProducts from './../components/Products/ExportProducts/ExportProducts'
import ImportProducts from './../components/Products/ImportProducts/ImportProducts'
import Login from './../components/Auth/Login/Login'
import AccountApi from './../components/Auth/AccountApi/AccountApi'
import AcceptTerms from './../components/Auth/AcceptTerms/AcceptTerms'
import Terms from './../components/Auth/Terms/Terms'
import GpcSelectDemo from './../components/Demo/GpcSelectDemo/GpcSelectDemo'

export default new Router({
    routes: [
        {
            path: '/',
            component: Layout,
            props: {
                showNavMenu: true
            },
            meta: {
                onlyAuth: true
            },
            children: [
                {
                    path: '/',
                    redirect: '/dashboard'
                },
                {
                    path: '/dashboard',
                    name: 'Dashboard',
                    component: Dashboard,
                    meta: {
                        pageTitle: 'Dashboard'
                    }
                },
                {
                    path: '/prefixes',
                    name: 'Prefixes',
                    component: Prefixes,
                    meta: {
                        breadcrumb: 'Prefixes',
                        pageTitle: 'Prefix management'
                    }
                },
                {
                    path: '/products',
                    name: 'ListProducts',
                    component: ListProducts,
                    meta: {
                        breadcrumb: 'My Products',
                        pageTitle: 'My Products'
                    }
                },
                {
                    path: '/products/add',
                    name: 'AddProduct',
                    component: AddProduct,
                    meta: {
                        breadcrumb: 'New Product',
                        pageTitle: 'New Product'
                    }
                },
                {
                    path: '/products/export',
                    name: 'ExportProducts',
                    component: ExportProducts,
                    meta: {
                        breadcrumb: 'Export',
                        pageTitle: 'Export Products'
                    }
                },
                {
                    path: '/products/import',
                    name: 'ImportProducts',
                    component: ImportProducts,
                    meta: {
                        breadcrumb: 'Import',
                        pageTitle: 'Import Products'
                    }
                }
            ]
        },
        {
            path: '/',
            component: Layout,
            children: [
                {
                    path: '/login',
                    component: Login,
                    meta: {
                        pageTitle: 'Auth.Stafflogin'
                    }
                },
                {
                    path: '/accept-terms',
                    component: AcceptTerms,
                    meta: {
                        pageTitle: 'Auth.AgreementRequired'
                    }
                },
                {
                    path: '/account-api',
                    component: AccountApi,
                    meta: {
                        pageTitle: 'Account API'
                    }
                },
                {
                    path: '/gpc-select-demo',
                    component: GpcSelectDemo,
                    meta: {
                        pageTitle: 'GPC Select Demo'
                    }
                },
                {
                    path: '/terms',
                    component: Terms,
                    meta: {
                        pageTitle: 'Auth.TermsAndConditions'
                    }
                }
            ]
        },
        {
            path: '/loginDjango',
            component: AppWait,
            meta: {
                pageTitle: 'Wait Login'
            }
        },]
})
