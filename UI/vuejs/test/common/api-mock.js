export default {
    countries: [{
            "id": 1,
            "code": "004",
            "name": "AFGHANISTAN"
        },
        {
            "id": 2,
            "code": "008",
            "name": "ALBANIA"
        },
        {
            "id": 3,
            "code": "012",
            "name": "ALGERIA"
        },
        {
            "id": 4,
            "code": "016",
            "name": "AMERICAN SAMOA"
        }
    ],
    packaging: [
        {
            "name": "0-gs1ie-Intermediate bulk container, rigid plastic",
            "order": 0,
            "package_level": 70,
            "member_organisation": "gs1ie",
            "package_type": 25,
            "image_url": "/static/products/site/wizard/proddesc/AA.png",
            "ui_label": "Intermediate bulk container, rigid plastic",
            "ui_description": "A Rigid Intermediate Bulk Container (RIBC) that is attached to a pallet or has the pallet integrated into the RIBC. The container is used for the transport and storage of fluids and other bulk materials."
        },
        {
            "name": "0-gs1ie-Aerosol",
            "order": 0,
            "package_level": 70,
            "member_organisation": "gs1ie",
            "package_type": 19,
            "image_url": "/static/products/site/wizard/proddesc/AE.png",
            "ui_label": "Aerosol",
            "ui_description": "A gas-tight, pressure-resistant container with a valve and propellant. When the valve is opened, propellant forces the product from the container in a fine or coarse spray pattern or stream. (e.g., a spray can dispensing paint, furniture polish, etc, under pressure). It does not include atomizers, because atomizers do not rely on a pressurised container to propel product from the container."
        },
        {
            "name": "0-gs1ie-Ampoule",
            "order": 0,
            "package_level": 70,
            "member_organisation": "gs1ie",
            "package_type": 26,
            "image_url": "http://undefined.com",
            "ui_label": "Ampoule",
            "ui_description": "A relatively small container made from glass or plastic tubing, the end of which is drawn into a stem and closed by fusion after filling. The bottom may be flat, convex, or drawn out. An ampule is opened by breaking the stem."
        },
        {
            "name": "0-gs1ie-Barrel",
            "order": 0,
            "package_level": 70,
            "member_organisation": "gs1ie",
            "package_type": 27,
            "image_url": "http://undefined.com",
            "ui_label": "Barrel",
            "ui_description": "A cylindrical packaging whose bottom end is permanently fixed to the body and top end (head) is either removable or non-removable."
        }
    ],
    templates: [
        {
            "name": "gs1ie-base",
            "order": 0,
            "package_level": 70,
            "attributes": [],
            "member_organisation": "gs1ie",
            "image_url": "/static/products/site/wizard/pos.png",
            "ui_label": "Consumer Unit (Base Unit/Each) e.g. bottle of beer"
        },
        {
            "name": "gs1ie-inner-pack",
            "order": 0,
            "package_level": 60,
            "attributes": [],
            "member_organisation": "gs1ie",
            "image_url": "/static/products/site/wizard/pack.png",
            "ui_label": "Pack or inner pack e.g. six pack of beer bottles"
        },
        {
            "name": "gs1ie-inner-case",
            "order": 0,
            "package_level": 50,
            "attributes": [],
            "member_organisation": "gs1ie",
            "image_url": "/static/products/site/wizard/case.png",
            "ui_label": "Case or mixed case e.g. case of beer (bottles or packs)"
        }
    ],
    targetMarketList: [
        {
            "id": 1,
            "code": "004",
            "market": "AFGHANISTAN"
        },
        {
            "id": 2,
            "code": "008",
            "market": "ALBANIA"
        },
        {
            "id": 3,
            "code": "012",
            "market": "ALGERIA"
        },
        {
            "id": 4,
            "code": "016",
            "market": "AMERICAN SAMOA"
        },
        {
            "id": 5,
            "code": "020",
            "market": "ANDORRA"
        }
    ],
    languageList: [
        {
            "id": 1,
            "slug": "en",
            "name": "English"
        },
        {
            "id": 53,
            "slug": "nl",
            "name": "Dutch"
        },
        {
            "id": 74,
            "slug": "fr",
            "name": "French"
        },
        {
            "id": 85,
            "slug": "de",
            "name": "German"
        }
    ],
    mock(server) {
        let promises = [];
        [
            [/\/api\/v1\/countries_of_origin\//, 'countries'],
            [/\/api\/v1\/packaging\/(.+)/, 'packaging'],
            [/\/api\/v1\/templates\/(.+)/, 'templates'],
            [/\/api\/v1\/target_markets\//, 'targetMarketList'],
            [/\/api\/v1\/languages\//, 'languageList']
        ].forEach(([regex, propName]) => {
            promises[propName] = new Promise((resolveFn) => {
                server.respondWith('GET', regex, (xhr, n) => {
                    xhr.respond(200, {
                        'Content-Type': 'application/json'
                    }, JSON.stringify(this[propName]));
                    resolveFn()
                });
            });
        });
        return promises;
    },
    mockUser(server) {
        return new Promise((resolveFn) => {
            server.respondWith('GET', /\/api\/v1\/accounts\/login\//, (xhr, n) => {
                xhr.respond(200, {
                    'Content-Type': 'application/json'
                }, JSON.stringify({
                    user: {
                        advanced_tab: true,
                        agreed: true,
                    }
                }));
                resolveFn();
            });
        });
    }
};
