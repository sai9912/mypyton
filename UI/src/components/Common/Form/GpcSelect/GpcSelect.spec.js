/* eslint-disable import/no-webpack-loader-syntax */
import {mount} from '@vue/test-utils'
import getTestEnv from '../../../../../tests/unit/utils/localVue'

import GpcSelectTest from './GpcSelect'
import FormConstants from '../FormConstants'

describe('GpcSelect.vue', () => {
  const testEnv = getTestEnv()
  let getList
  let clock
  beforeEach(() => {
    clock = sinon.useFakeTimers()
    getList = sinon.stub().resolves([{Brick: 'Brick', BrickCode: 'BrickCode'}])
    GpcSelectTest.__Rewire__('GPCServices', {
      getList: getList
    })
  })
  afterEach(function () {
    clock.restore()
  })

  it('should load send correct params', (done) => {
    const wrapper = mount(GpcSelectTest, {
      ...testEnv
    })
    wrapper.vm.onSearch('12345', () => {
    })

    setTimeout(() => {
      wrapper.vm.onSearch('code', () => {
      })
      setTimeout(() => {
        expect(getList.args).to.deep.equal([
          [{brick_code: '12345'}],
          [{brick: 'code'}]
        ])
        done()
      }, FormConstants.SEARCH_TIMEOUT + 1)
      clock.tick(FormConstants.SEARCH_TIMEOUT + 2)
    }, FormConstants.SEARCH_TIMEOUT + 1)
    clock.tick(FormConstants.SEARCH_TIMEOUT + 2)
  })

  it('should not send query if search length less 3', (done) => {
    const wrapper = mount(GpcSelectTest, {
      ...testEnv
    })
    wrapper.vm.onSearch('12', () => {
    })

    setTimeout(() => {
      expect(getList.called).to.equal(false)
      done()
    }, FormConstants.SEARCH_TIMEOUT + 1)
    clock.tick(FormConstants.SEARCH_TIMEOUT + 2)
  })
  it('should send query if search length more 2', (done) => {
    const wrapper = mount(GpcSelectTest, {
      ...testEnv
    })
    wrapper.vm.onSearch('123', () => {
    })

    setTimeout(() => {
      expect(getList.called).to.equal(true)
      done()
    }, FormConstants.SEARCH_TIMEOUT + 1)
    clock.tick(FormConstants.SEARCH_TIMEOUT + 2)
  })
})
