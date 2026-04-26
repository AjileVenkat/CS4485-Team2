import { classList } from '../../utils/classList'

const Panel = ({ as, className, children, ...props }) => {
  const Tag = as ?? 'article'

  return (
    <Tag className={classList('panel p-6', className)} {...props}>
      {children}
    </Tag>
  )
}

export default Panel
