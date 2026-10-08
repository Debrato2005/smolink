import { useCallback } from 'react';
import { Link, useParams, useSearchParams } from 'react-router';
import type { ProductGateway } from '../../lib/api/contracts';
import { useResource } from '../../lib/useResource';
import { ErrorNotice, Loading } from '../../components/ui/Feedback';
import { Icon } from '../../components/ui/Icon';
export function Analytics({
  links,
  revision,
}: {
  links: ProductGateway;
  revision: number;
}) {
  const { id = '' } = useParams();
  const [params, setParams] = useSearchParams();
  const days = params.get('range') === '30' ? 30 : 7;
  const load = useCallback(
    async (signal: AbortSignal) => {
      void revision;
      const [link, report] = await Promise.all([
        links.get(id, signal),
        links.analytics(id, days, signal),
      ]);
      return { link, report };
    },
    [links, id, days, revision],
  );
  const { data, error, loading, reload } = useResource(load);
  const total =
    data?.report.daily.reduce((sum, row) => sum + row.clicks, 0) ?? 0;
  const max = Math.max(1, ...(data?.report.daily.map((d) => d.clicks) ?? []));
  return (
    <>
      <Link className="back-link" to={`/dashboard/urls/${id}`}>
        <Icon name="back" size={17} />
        Link details
      </Link>
      <div className="page-heading">
        <div>
          <h1>Link analytics</h1>
          <p className="muted">Every click is a little connection.</p>
        </div>
        <div className="filter-field">
          <label htmlFor="range">Date range</label>
          <select
            id="range"
            value={days}
            onChange={(e) => setParams({ range: e.target.value })}
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>
      </div>
      {loading ? (
        <Loading label="Loading analytics…" />
      ) : error ? (
        <ErrorNotice error={error} retry={reload} />
      ) : (
        data && (
          <>
            <p className="report-provenance">
              <span className="mono break-word">/{data.link.shortCode}</span>
              <span>
                {data.report.daily[0]?.date} to {data.report.daily.at(-1)?.date}{' '}
                (UTC)
              </span>
            </p>
            <div className="ledger">
              <dl>
                <div>
                  <dt>Clicks in this range</dt>
                  <dd>{total.toLocaleString()}</dd>
                </div>
                <div>
                  <dt>Daily average</dt>
                  <dd>{(total / days).toFixed(1)}</dd>
                </div>
                <div>
                  <dt>Peak day</dt>
                  <dd>{total ? max : 0}</dd>
                </div>
              </dl>
            </div>
            <section className="chart-panel">
              <div className="panel-heading">
                <h2>A little momentum.</h2>
                <span className="small muted">
                  Clicks per day, UTC. Yellow marks the peak.
                </span>
              </div>
              {total === 0 && <p>No clicks in this range yet.</p>}
              <div
                className="bar-chart"
                role="img"
                aria-label={`${total} clicks across ${days} days. Peak ${total ? max : 0} clicks. Exact values appear in the daily clicks table.`}
              >
                {data.report.daily.map((row) => (
                  <div className="bar-column" key={row.date}>
                    <span className="bar-value">
                      {days === 7 ? row.clicks : ''}
                    </span>
                    <div className="bar-space">
                      <div
                        className={
                          total && row.clicks === max
                            ? 'chart-bar chart-peak'
                            : 'chart-bar'
                        }
                        style={{ height: `${(row.clicks / max) * 100}%` }}
                      />
                    </div>
                    <span className="bar-date">
                      {days === 7 ? row.date.slice(5) : ''}
                    </span>
                  </div>
                ))}
              </div>
              <p className="small muted">
                Updated{' '}
                {new Date(data.report.updatedAt).toLocaleString('en', {
                  timeZone: 'UTC',
                })}{' '}
                UTC.
              </p>
            </section>
            <div className="breakdown-grid">
              {[
                {
                  title: 'Where clicks come from',
                  rows: data.report.referrers,
                },
                { title: 'How people visit', rows: data.report.devices },
              ].map(({ title, rows }) => (
                <section className="breakdown" key={title}>
                  <h2>{title}</h2>
                  <table>
                    <thead>
                      <tr>
                        <th>Source</th>
                        <th>Clicks</th>
                        <th>Share</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row) => (
                        <tr key={row.name}>
                          <td>{row.name}</td>
                          <td>{row.clicks.toLocaleString()}</td>
                          <td>
                            {total ? Math.round((row.clicks / total) * 100) : 0}
                            %
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </section>
              ))}
            </div>
            <details className="daily-data" open>
              <summary>
                View daily data
                <Icon name="plus" />
              </summary>
              <div
                className="daily-table-wrap"
                role="region"
                aria-label="Daily clicks data"
                tabIndex={0}
              >
                <table aria-label="Daily clicks">
                  <thead>
                    <tr>
                      <th>Date (UTC)</th>
                      <th>Clicks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.report.daily.map((row) => (
                      <tr key={row.date}>
                        <td>{row.date}</td>
                        <td>{row.clicks}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          </>
        )
      )}
    </>
  );
}
