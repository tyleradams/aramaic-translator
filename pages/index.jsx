import React from 'react';
import Head from 'next/head';
import 'bootstrap/dist/css/bootstrap.min.css';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import tableify from 'tableify';
import parse from 'html-react-parser';

const renderRule = (rule) => (
    <tr>
      <td>{rule.type}</td>
      <td>{parse(tableify(rule[rule.type]))}</td>
    </tr>
);

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      translationResults: [],
      inputText: '',
      weakMatch: false,
    };
    this.fetchResults = this.fetchResults.bind(this);
    this.inputTextChange = this.inputTextChange.bind(this);
    this.weakMatchChange = this.weakMatchChange.bind(this);
  }

  fetchResults() {
    const body = {
      method: 'POST',
      body: JSON.stringify({ word: this.state.inputText, weak_match: this.state.weakMatch }),
      headers: {
        'Content-Type': 'application/json',
      },
    };
    fetch('http://localhost:5000/api/translator', body).then((r) => r.json()).then((r) => {
      this.setState({ translationResults: r.words });
    });
  }

  weakMatchChange() {
    this.setState({ weakMatch: !this.state.weakMatch });
  }

  inputTextChange(e) {
    this.setState({ inputText: e.target.value });
  }

  render() {
    const renderTranslation = (r) => (
        <Table striped bordered>
          <tbody>
              <tr>
                  <td>Full word</td>
                  <td>{r.word}</td>
              </tr>
            <tr>
              <td>meaning</td>
              <td>{r.root.meaning}</td>
            </tr>
            <tr>
              <td>root-type</td>
              <td>{r.root['root-type']}</td>
            </tr>
            {r.rules.map(renderRule)}
          </tbody>
        </Table>
    );
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
          <div>
            <div className="d-flex">
              Word
              <div>
                <input type="text" value={this.state.inputText} onChange={this.inputTextChange} className="translation-input--text"/><br />
              </div>
            </div>
            <div className="d-flex">
              Weak Match
              <div className="ml-4 text-right">
                <input type="checkbox" value={this.state.weakMatch} onChange={this.weakMatchChange} className="float-right translation-input--text"/>
              </div>
            </div>
            <Button value="Translate" className="translation-input--translate-button" onClick={this.fetchResults}>Translate</Button>
          </div>
          <div className="translator-output--container">
            Returned {this.state.translationResults.length} Results
            {this.state.translationResults.map(renderTranslation)}
          </div>

        </main>
      </div>
    );
  }
}
export default Home;
