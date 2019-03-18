/* eslint-disable import/no-webpack-loader-syntax */
const prefixesModuleInjector = require('inject-loader!./prefixes.js')
describe('prefixes.module', () => {
  describe('mutations', () => {
    const prefixModule = prefixesModuleInjector().default
    it('updatePrefixes', () => {
      const {updatePrefixes} = prefixModule.mutations
      const state = {prefixes: null}
      const prefixes = [{
        id: 'prefix'
      }]
      updatePrefixes(state, prefixes)
      expect(state.prefixes).to.equal(prefixes)
    })

    it('setActivePrefix', () => {
      const {setActivePrefix} = prefixModule.mutations
      const state = {
        activePrefix: null,
        activePrefixId: null
      }

      const prefix = {prefix: 'prefix'}
      setActivePrefix(state, prefix)
      expect(state.activePrefix).to.equal(prefix)
      expect(state.activePrefixId).to.equal(prefix.prefix)
    })

    it('resetActivePrefix', () => {
      const {resetActivePrefix} = prefixModule.mutations
      const state = {
        activePrefix: {prefix: 'prefix'},
        activePrefixId: 'prefix'
      }

      resetActivePrefix(state)

      expect(state.activePrefix).to.equal(null)
      expect(state.activePrefixId).to.equal(null)
    })
    it('setLoading', () => {
      const {setLoading} = prefixModule.mutations
      const state = {
        loading: false
      }

      setLoading(state, true)
      expect(state.loading).to.equal(true)
    })
  })
  describe('actions', () => {
    const firstPrefix = {
      id: 'prefix1'
    }
    const secondPrefix = {
      id: 'prefix1'
    }
    const prefixes = [
      firstPrefix,
      secondPrefix
    ]
    const prefixModule = prefixesModuleInjector({
      '../../services/PrefixesService': {
        getList: sinon.stub().resolves(prefixes)
      }
    }).default

    it('loadPrefixes - should load data', (done) => {
      const {actions} = prefixModule
      const commit = sinon.spy()
      const state = {
        loading: false,
        prefixes: [],
        activePrefix: null,
        activePrefixId: false
      }
      actions.loadPrefixes({commit, state})
      setTimeout(() => {
        expect(commit.args[0]).to.deep.equal(['setLoading', true])
        expect(commit.args[1]).to.deep.equal(['updatePrefixes', prefixes])
        expect(commit.args[3]).to.deep.equal(['setLoading', false])
        done()
      })
    })
    it('loadPrefixes - select default prefix', (done) => {
      const {actions} = prefixModule
      const commit = sinon.spy()
      const state = {
        loading: false,
        prefixes: [],
        activePrefix: null,
        activePrefixId: 'old_prefix'
      }
      actions.loadPrefixes({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['setLoading', true],
          ['updatePrefixes', prefixes],
          ['setActivePrefix', firstPrefix],
          ['setLoading', false]
        ])
        done()
      })
    })
    it('loadPrefixes - select active prefix', (done) => {
      const {actions} = prefixModule
      const commit = sinon.spy()
      const state = {
        loading: false,
        prefixes: [],
        activePrefix: null,
        activePrefixId: 'prefix2'
      }
      actions.loadPrefixes({commit, state})
      setTimeout(() => {
        expect(commit.args).to.deep.equal([
          ['setLoading', true],
          ['updatePrefixes', prefixes],
          ['setActivePrefix', secondPrefix],
          ['setLoading', false]
        ])
        done()
      })
    })
  })
})
