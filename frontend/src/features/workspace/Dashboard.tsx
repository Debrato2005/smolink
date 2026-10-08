import { useCallback } from 'react';
import { Link, useSearchParams } from 'react-router';
import type { ProductGateway } from '../../lib/api/contracts';
import { useResource } from '../../lib/useResource';
import { linkStatus } from '../../lib/validation';
import { Button } from '../../components/ui/Button';
import { Icon } from '../../components/ui/Icon';
import { ErrorNotice, Loading } from '../../components/ui/Feedback';
import { LinkActions } from '../shorten/LinkActions';

export function Dashboard({
  links,
  revision,
}: {
  links: ProductGateway;
  revision: number;
}) {
  const load = useCallback(
    (signal: AbortSignal) => {
      void revision;
      return links.list(signal);
    },
    [links, revision],
  );
  const { data, error, loading, reload } = useResource(load);
  const [params, setParams] = useSearchParams();
  const query = params.get('q') ?? '';
  const status = params.get('status') ?? 'all';
  const sort = params.get('sort') ?? 'newest';
  const overview = params.get('view') === 'analytics';
  // Read the committed URL, not the hook value. Router navigations run as
  // transitions, so the hook value can lag one quick edit behind and a second
  // edit would then overwrite the first.
  function update(change: (next: URLSearchParams) => void, replace = false) {
    const next = new URLSearchParams(window.location.search);
    change(next);
    setParams(next, { replace });
  }
  function filter(name: string, value: string) {
    update((next) => {
      if (value) next.set(name, value);
      else next.delete(name);
      next.delete('page');
    }, true);
  }
  const filtered = (data ?? [])
    .filter(
      (row) =>
        `${row.shortCode} ${row.destination}`
          .toLowerCase()
          .includes(query.toLowerCase()) &&
        (status === 'all' || linkStatus(row).toLowerCase() === status),
    )
    .sort((a, b) =>
      sort === 'clicks'
        ? b.clicks - a.clicks
        : sort === 'oldest'
          ? a.createdAt.localeCompare(b.createdAt)
          : b.createdAt.localeCompare(a.createdAt),
    );
  const pages = Math.max(1, Math.ceil(filtered.length / 6));
  const requestedPage = Number(params.get('page'));
  const page = Number.isSafeInteger(requestedPage)
    ? Math.min(pages, Math.max(1, requestedPage))
    : 1;
  const rows = filtered.slice((page - 1) * 6, page * 6);
  const totalClicks = data?.reduce((sum, row) => sum + row.clicks, 0) ?? 0;
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>{overview ? 'The bigger picture.' : 'Your links'}</h1>
          <p className="muted">
            {overview
              ? 'A little perspective on what you share.'
              : 'Everything you share, all in one place.'}
          </p>
        </div>
        <Link className="button-link" to="/dashboard/new">
          <Icon name="plus" />
          Create link
        </Link>
      </div>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorNotice error={error} retry={reload} />
      ) : (
        data && (
          <>
            <div className="ledger">
              <dl>
                <div>
                  <dt>Total links</dt>
                  <dd>{data.length}</dd>
                </div>
                <div>
                  <dt>Lifetime clicks</dt>
                  <dd>{totalClicks.toLocaleString()}</dd>
                </div>
                <div>
                  <dt>Active links</dt>
                  <dd>
                    {data.filter((r) => linkStatus(r) === 'Active').length}
                  </dd>
                </div>
              </dl>
            </div>
            {overview && (
              <section className="overview-panel">
                <h2>Your most visited links</h2>
                <p className="muted small">
                  Lifetime clicks. Select a link for its daily report.
                </p>
                <div className="ranked-links">
                  {[...data]
                    .sort((a, b) => b.clicks - a.clicks)
                    .slice(0, 5)
                    .map((row) => (
                      <Link
                        key={row.linkId}
                        to={`/dashboard/urls/${row.linkId}/analytics`}
                      >
                        <span>{row.shortCode}</span>
                        <span className="rank-track">
                          <span
                            style={{
                              width: `${totalClicks ? (row.clicks / Math.max(...data.map((r) => r.clicks))) * 100 : 0}%`,
                            }}
                          />
                        </span>
                        <strong>{row.clicks.toLocaleString()}</strong>
                        <Icon name="arrow" size={17} />
                      </Link>
                    ))}
                </div>
              </section>
            )}
            <section className="links-panel" aria-label="Saved links">
              <div className="table-toolbar">
                <div className="search-field">
                  <Icon name="search" />
                  <input
                    aria-label="Search links"
                    type="search"
                    placeholder="Search links or destinations…"
                    value={query}
                    onChange={(e) => filter('q', e.target.value)}
                  />
                </div>
                <div className="filter-field">
                  <label htmlFor="status-filter">Status</label>
                  <select
                    id="status-filter"
                    value={status}
                    onChange={(e) => filter('status', e.target.value)}
                  >
                    <option value="all">All statuses</option>
                    <option value="active">Active</option>
                    <option value="paused">Paused</option>
                    <option value="expired">Expired</option>
                  </select>
                </div>
                <div className="filter-field">
                  <label htmlFor="sort-filter">Sort by</label>
                  <select
                    id="sort-filter"
                    value={sort}
                    onChange={(e) => filter('sort', e.target.value)}
                  >
                    <option value="newest">Newest first</option>
                    <option value="oldest">Oldest first</option>
                    <option value="clicks">Most clicks</option>
                  </select>
                </div>
              </div>
              {rows.length ? (
                <>
                  <table className="link-table">
                    <thead>
                      <tr>
                        <th>Short link / destination</th>
                        <th>Status</th>
                        <th>Clicks</th>
                        <th>Created</th>
                        <th>
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row) => (
                        <tr key={row.linkId}>
                          <td>
                            <div className="link-cell">
                              <div>
                                <Link
                                  className="short-code"
                                  to={`/dashboard/urls/${row.linkId}`}
                                >
                                  {row.shortCode}
                                </Link>
                                <span
                                  className="destination-text"
                                  title={row.destination}
                                >
                                  {row.destination.replace(/^https?:\/\//, '')}
                                </span>
                              </div>
                            </div>
                          </td>
                          <td>
                            <span
                              className={`status-label status-${linkStatus(row).toLowerCase()}`}
                            >
                              <span aria-hidden="true" />
                              {linkStatus(row)}
                            </span>
                          </td>
                          <td className="numeric">
                            <span className="mobile-label">Clicks </span>
                            {row.clicks.toLocaleString()}
                          </td>
                          <td className="date-cell">
                            {new Intl.DateTimeFormat('en', {
                              month: 'short',
                              day: 'numeric',
                              timeZone: 'UTC',
                            }).format(new Date(row.createdAt))}
                          </td>
                          <td>
                            <LinkActions compact link={row} links={links} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="pagination">
                    <p aria-live="polite">
                      Showing {(page - 1) * 6 + 1}–
                      {Math.min(page * 6, filtered.length)} of {filtered.length}{' '}
                      links
                    </p>
                    <div>
                      <Button
                        className="button-secondary button-small"
                        disabled={page === 1}
                        aria-label="Previous page"
                        onClick={() =>
                          update((next) => next.set('page', String(page - 1)))
                        }
                      >
                        <Icon name="back" size={16} />
                      </Button>
                      <span>
                        Page {page} of {pages}
                      </span>
                      <Button
                        className="button-secondary button-small"
                        disabled={page === pages}
                        aria-label="Next page"
                        onClick={() =>
                          update((next) => next.set('page', String(page + 1)))
                        }
                      >
                        <Icon name="arrow" size={16} />
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <Icon
                    name={query || status !== 'all' ? 'search' : 'link'}
                    size={40}
                  />
                  <h2>
                    {query || status !== 'all'
                      ? 'No matching links'
                      : 'A little empty. A lot of possibility.'}
                  </h2>
                  <p>
                    {query || status !== 'all'
                      ? 'Try a different search or clear your filters.'
                      : 'Create your first link and give it a home here.'}
                  </p>
                  {query || status !== 'all' ? (
                    <Button
                      className="button-secondary"
                      onClick={() => setParams({})}
                    >
                      Clear filters
                    </Button>
                  ) : (
                    <Link className="button-link" to="/dashboard/new">
                      Create link
                      <Icon name="plus" />
                    </Link>
                  )}
                </div>
              )}
            </section>
          </>
        )
      )}
    </>
  );
}
