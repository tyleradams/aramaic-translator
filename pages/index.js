import React, {useState} from 'react'
import Head from 'next/head'

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      translationResults: [],
      inputText: "",
      weakMatch: false,
    }
    this.fetchResults = this.fetchResults.bind(this);
    this.inputTextChange = this.inputTextChange.bind(this);
    this.weakMatchChange = this.weakMatchChange.bind(this);
    this.renderRule = this.renderRule.bind(this);
  }

  fetchResults() {
    const body = {
      method: 'POST',
        body: JSON.stringify({ word: this.state.inputText, weak_match: this.state.weakMatch }),
      headers: {
        'Content-Type': 'application/json'
      }
    };
    fetch(`api/translator`, body).then(r => r.json()).then(r => {
      this.setState({translationResults: r.words})
      console.log(r.words)
    })
  }

  weakMatchChange(e) {
    this.setState({weakMatch: !this.state.weakMatch});
  }

  inputTextChange(e) {
    this.setState({inputText: e.target.value});
  }

  renderRule(rule, key) {
    if (typeof(rule[rule.type]) === "string") {
      return (
        <tr key={key}>
          <td>{rule.type}</td>
          <td>{rule[rule.type]}</td>
        </tr>
      )
    } else {
      return (
        <tr key={key}>
          <td>{rule.type}</td>
          <td>{JSON.stringify(rule[rule.type])}</td>
        </tr>
      )
    }
  }

  render() {
    return (
      <div className="container">
        <Head>
          <title>Aramaic Translator</title>
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <main>
          <h1 className="title">
            Translate Aramaic
          </h1>
          <form>
            <input type="text" value={this.state.inputText} onChange={this.inputTextChange} className="translation-input--text"/>
            <input type="checkbox" value={this.state.weakMatch} onChange={this.weakMatchChange} className="translation-input--text"/>
            <input type="button" value="Translate" className="translation-input--translate-button" onClick={this.fetchResults}/>
          </form>
          <div className="translator-output--container">
            {this.state.translationResults.map((r,i) => {
              return (
              <table key={i} className="table">
                <thead>
                  <tr><td>{r.word}</td></tr>
                  <tr>
                    <td>meaning</td>
                    <td>{r.root.meaning}</td>
                  </tr>
                  <tr>
                    <td>root-type</td>
                    <td>{r.root["root-type"]}</td>
                  </tr>
                </thead>
                <tbody>
                  {r.rules.map(this.renderRule)}
                </tbody>
              </table>
            )})}
          </div>


        </main>

        <style jsx>{`
          .container {
            min-height: 100vh;
            padding: 0 0.5rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
          }

          main {
            padding: 5rem 0;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
          }

          footer {
            width: 100%;
            height: 100px;
            border-top: 1px solid #eaeaea;
            display: flex;
            justify-content: center;
            align-items: center;
          }

          footer img {
            margin-left: 0.5rem;
          }

          footer a {
            display: flex;
            justify-content: center;
            align-items: center;
          }

          a {
            color: inherit;
            text-decoration: none;
          }

          .title a {
            color: #0070f3;
            text-decoration: none;
          }

          .title a:hover,
          .title a:focus,
          .title a:active {
            text-decoration: underline;
          }

          .title {
            margin: 0;
            line-height: 1.15;
            font-size: 4rem;
          }

          .title,
          .description {
            text-align: center;
          }

          .description {
            line-height: 1.5;
            font-size: 1.5rem;
          }

          code {
            background: #fafafa;
            border-radius: 5px;
            padding: 0.75rem;
            font-size: 1.1rem;
            font-family: Menlo, Monaco, Lucida Console, Liberation Mono,
              DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace;
          }

          .grid {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;

            max-width: 800px;
            margin-top: 3rem;
          }

          .card {
            margin: 1rem;
            flex-basis: 45%;
            padding: 1.5rem;
            text-align: left;
            color: inherit;
            text-decoration: none;
            border: 1px solid #eaeaea;
            border-radius: 10px;
            transition: color 0.15s ease, border-color 0.15s ease;
          }

          .card:hover,
          .card:focus,
          .card:active {
            color: #0070f3;
            border-color: #0070f3;
          }

          .card h3 {
            margin: 0 0 1rem 0;
            font-size: 1.5rem;
          }

          .card p {
            margin: 0;
            font-size: 1.25rem;
            line-height: 1.5;
          }

          .logo {
            height: 1em;
          }

          @media (max-width: 600px) {
            .grid {
              width: 100%;
              flex-direction: column;
            }
          }
        `}</style>

        <style jsx global>{`
          html,
          body {
            padding: 0;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto,
              Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue,
              sans-serif;
          }

          * {
            box-sizing: border-box;
          }
        `}</style>
      </div>
    )
  }
}
export default Home;
