/* eslint-disable import/no-webpack-loader-syntax */

import moment from 'moment'

const authModuleInjector = require('inject-loader!./auth.js')
describe('auth.module', () => {
  describe('mutations', () => {
    const authModule = authModuleInjector().default
    it('updateData', () => {
      const {updateData} = authModule.mutations
      const state = {usedData: null}
      const userData = {
        userName: 'aaa'
      }
      updateData(state, userData)

      expect(state.userData).to.equal(userData)
    })

    it('updateToken', () => {
      const {updateToken} = authModule.mutations
      const state = {
        token: null,
        expired: null,
        lastRenew: null
      }

      const token = 'token'
      updateToken(state, token)
      expect(state.token).to.equal(token)
      expect(state.isAuth).to.equal(true)
    })

    it('rememberMe', () => {
      const {rememberMe} = authModule.mutations
      const state = {rememberMe: false}

      rememberMe(state, true)

      expect(state.rememberMe).to.equal(true)
    })
    it('logout', () => {
      const {logout} = authModule.mutations
      const state = {
        userData: {
          userName: 'aaa'
        },
        token: 'token',
        isAuth: true
      }
      logout(state)
      expect(state).to.deep.equal({
        userData: null,
        token: null,
        isAuth: false,
        needAcceptTerms: false
      })
    })

    it('setTerms', () => {
      const {setTerms} = authModule.mutations
      const state = {
        terms: null
      }
      const terms = {}
      setTerms(state, terms)
      expect(state.terms).to.equal(terms)
    })
    it('setNeedAcceptTerms', () => {
      const {setNeedAcceptTerms} = authModule.mutations
      const state = {
        needAcceptTerms: false
      }
      setNeedAcceptTerms(state, true)
      expect(state.needAcceptTerms).to.equal(true)
    })
  })
  describe('actions', () => {
    const token = 'token'
    const user = {
      userName: 'aaa'
    }
    const answer = {
      token,
      user
    }

    let authModule = authModuleInjector({
      '../../services/AuthService': {
        login: sinon.stub().resolves(answer),
        renew: sinon.stub().resolves({token})
      }
    }).default

    it('login with new terms', (done) => {
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {
        userData: null,
        token: null,
        isAuth: false
      }
      actions.login({commit, state}, {
        username: 'username',
        password: 'password',
        rememberMe: false
      })
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['updateToken', token],
          ['updateData', user],
          ['rememberMe', false]
        ])
        done()
      })
    })
    it('login', (done) => {
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {
        userData: null,
        token: null,
        isAuth: false
      }
      actions.login({commit, state}, {
        username: 'username',
        password: 'password',
        rememberMe: false
      })
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['updateToken', token],
          ['updateData', user],
          ['rememberMe', false]
        ])
        done()
      })
    })
    it('logout', (done) => {
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {
        userData: null,
        token: null,
        isAuth: true
      }
      actions.logout({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['logout']
        ])
        done()
      })
    })
    it('inspectToken', (done) => {
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {
        token: 'token1',
        expired: moment().add(5, 'minutes'),
        nextRenew: moment().add(-1, 'minutes')
      }
      actions.inspectToken({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['updateToken', token]
        ])
        done()
      })
    })

    it('checkTerms - accept first login', (done) => {
      const terms =
        {
          'date_terms': moment().toDate(),
          'date_terms_cloud': moment().toDate()
        }
      const authModule = authModuleInjector({
        '../../services/AuthService': {
          getTerms: sinon.stub().resolves(terms)
        }
      }).default
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {
        userData: {
          agreed: false,
          agreed_version: moment().toDate()
        }
      }
      actions.checkTerms({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['setTerms', terms],
          ['setNeedAcceptTerms', true]
        ])
        done()
      })
    })

    it('checkTerms - accept later version', (done) => {
      const terms =
        {
          'date_terms': moment().toDate(),
          'date_terms_cloud': moment().toDate()
        }
      const authModule = authModuleInjector({
        '../../services/AuthService': {
          getTerms: sinon.stub().resolves(terms)
        }
      }).default
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {

        userData: {
          agreed: true,
          agreed_version: moment().add(-5, 'days').toDate()
        }
      }
      actions.checkTerms({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['setTerms', terms],
          ['setNeedAcceptTerms', true]
        ])
        done()
      })
    })

    it('checkTerms - not accept old version', (done) => {
      const terms =
        {
          'date_terms': moment().toDate(),
          'date_terms_cloud': moment().toDate()
        }
      const authModule = authModuleInjector({
        '../../services/AuthService': {
          getTerms: sinon.stub().resolves(terms)
        }
      }).default
      const {actions} = authModule
      const commit = sinon.spy()
      const state = {

        userData: {
          agreed: true,
          agreed_version: moment().add(5, 'days').toDate()
        }
      }
      actions.checkTerms({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['setTerms', terms]
        ])
        done()
      })
    })

    it('acceptTerms', (done) => {
      const patch = sinon.stub().resolves({})
      const authModule = authModuleInjector({
        '../../services/AuthService': {
          patch: patch
        }
      }).default
      const {actions} = authModule
      const commit = sinon.spy()
      const email = 'aaa'
      const dataTerms = moment().format()
      const state = {
        userData: {
          email: email
        },
        terms: {
          date_terms: dataTerms,
          date_terms_cloud: moment().format()
        }
      }
      actions.acceptTerms({commit, state})
      setTimeout(() => {
        expect(patch).to.deep.have.been.calledWith(email, {
          agreed: true, agreed_version: dataTerms, agreed_date: moment().utc().format()
        })
        expect(commit.args).to.deep.equal([
          ['setNeedAcceptTerms', false]
        ])
        done()
      })
    })
  })
})
