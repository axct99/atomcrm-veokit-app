const { React, moment, com } = window.globalEnv
const { view, app } = window.localEnv
const { useState, useEffect, useMemo } = React

const { content, strs } = view.data

const TokenModal = ({ opened, closeTokenModal }) => {
  const [token, setToken] = useState(null)
  const [reqLoading, setReqLoading] = useState(false)

  const getToken = () => {
    setReqLoading(true)
    app
      .sendReq('getToken', {})
      .then(result => {
        setReqLoading(false)

        if (result.res == 'ok') {
          setToken(result.token)
        }
      })
  }

  return {
    _com: 'Modal',
    opened,
    onCancel: () => closeTokenModal(),
    title: strs['tokenModal_title'],
    subtitle: strs['tokenModal_subtitle'],
    content: [
      {
        _com: 'Button',
        _vis: !token,
        type: 'primary',
        label: strs['tokenModal_createToken'],
        onClick: () => getToken(),
        loading: reqLoading
      },
      {
        _com: 'Field.Input',
        _vis: !!token,
        value: token,
        label: strs['tokenModal_token'],
        multiline: true,
        type: 'text',
        readOnly: true
      }
    ]
  }
}

view.render = () => {
  const [tokenModal, setTokenModal] = useState({
    opened: false
  })

  const closeTokenModal = () => {
    setTokenModal({
      ...tokenModal,
      opened: false
    })
  }

  view.methods.openToken = () => {
    setTokenModal({
      ...tokenModal,
      opened: true
    })
  }

  return {
    header: view.header,
    scheme: [
      {
        _com: 'Information',
        content
      },
      TokenModal({
        ...tokenModal,
        closeTokenModal
      })
    ]
  }
}
